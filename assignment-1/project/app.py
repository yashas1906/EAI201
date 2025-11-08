import heapq
import requests
import json
from flask import Flask, render_template, jsonify, request
from database import campus_map, coordinates, building_info, faq_data

app = Flask(__name__)

# --- Search Algorithms ---
def bfs(graph, start, goal):
    if start not in graph or goal not in graph: return None, 0, 0
    q = [(start, [start])]; visited = {start}
    nodes_explored = 0
    while q:
        nodes_explored += 1; current, path = q.pop(0)
        if current == goal:
            dist = sum(graph[path[i]][path[i+1]] for i in range(len(path) - 1))
            return path, dist, nodes_explored
        for neighbor in graph[current]:
            if neighbor not in visited: visited.add(neighbor); q.append((neighbor, path + [neighbor]))
    return None, 0, 0

def dfs(graph, start, goal):
    if start not in graph or goal not in graph: return None, 0, 0
    stack = [(start, [start])]; visited = set()
    nodes_explored = 0
    while stack:
        nodes_explored += 1; current, path = stack.pop()
        if current == goal:
            dist = sum(graph[path[i]][path[i+1]] for i in range(len(path) - 1))
            return path, dist, nodes_explored
        if current not in visited:
            visited.add(current)
            for neighbor in reversed(list(graph[current])):
                if neighbor not in visited: stack.append((neighbor, path + [neighbor]))
    return None, 0, 0

def ucs(graph, start, goal):
    if start not in graph or goal not in graph: return None, 0, 0
    pq = [(0, start, [start])]; visited = set()
    nodes_explored = 0
    while pq:
        nodes_explored += 1; cost, current, path = heapq.heappop(pq)
        if current == goal: return path, cost, nodes_explored
        if current not in visited:
            visited.add(current)
            for neighbor, distance in graph[current].items():
                if neighbor not in visited: heapq.heappush(pq, (cost + distance, neighbor, path + [neighbor]))
    return None, 0, 0

def a_star(graph, start, goal, coords):
    def heuristic(n1, n2):
        x1, y1 = coords[n1]; x2, y2 = coords[n2]
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5 * 111000
    if start not in graph or goal not in graph: return None, 0, 0
    pq = [(heuristic(start, goal), 0, start, [start])]; visited = set()
    nodes_explored = 0
    while pq:
        nodes_explored += 1; _, cost, current, path = heapq.heappop(pq)
        if current == goal: return path, cost, nodes_explored
        if current not in visited:
            visited.add(current)
            for neighbor, distance in graph[current].items():
                if neighbor not in visited:
                    new_cost = cost + distance
                    heapq.heappush(pq, (new_cost + heuristic(neighbor, goal), new_cost, neighbor, path + [neighbor]))
    return None, 0, 0

def get_campus_context():
    location_list = ", ".join(f'"{name}"' for name in building_info.keys())
    context = (
        "You are BotBrain, a helpful AI assistant. Your primary expertise is Chanakya University. "
        "When asked about the campus, you must use the following information to answer accurately. "
        "However, you are also a general AI, so you can answer questions about any other topic as well.\n\n"
        "== CAMPUS KNOWLEDGE BASE ==\n"
    )
    for name, info in building_info.items():
        context += f"- {name}: {info['Information']} Timings: {info['Timings']}.\n"
    for q, a in faq_data.items():
        context += f"- User question '{q}': Your answer '{a}'\n"
    context += (
        "\n== SPECIAL COMMANDS ==\n"
        "You have special actions. If the user's request matches an action, you MUST respond with ONLY the corresponding JSON object.\n"
        "1. NAVIGATION: If the user asks for directions or a path (e.g., 'go from X to Y'), respond with this exact JSON format. Available locations: " + location_list + ".\n"
        '   Format: {"action": "navigate", "parameters": {"start": "START_LOCATION", "end": "END_LOCATION"}}\n'
        "2. RESET: If the user asks to 'reset', 'clear', or 'start over', respond with this exact JSON format:\n"
        '   Format: {"action": "reset"}\n\n'
        "For all other requests, provide a helpful, conversational answer."
    )
    return context

# --- API Endpoints ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/locations')
def get_locations(): return jsonify(coordinates)

@app.route('/api/navigate', methods=['POST'])
def navigate():
    data = request.json
    start, end, algorithm = data.get('start'), data.get('end'), data.get('algorithm')
    path, distance, nodes_explored, algo_name = None, 0, 0, ''

    if algorithm == 'find_best':
        results = []
        algos_to_run = {
            'BFS': bfs(campus_map, start, end), 'DFS': dfs(campus_map, start, end),
            'UCS': ucs(campus_map, start, end), 'A* Search': a_star(campus_map, start, end, coordinates)
        }
        for name, (p, d, n) in algos_to_run.items():
            if p: results.append({'name': name, 'path': p, 'distance': d, 'nodes': n})
        if not results: return jsonify({'error': 'No path found.'}), 404
        best_result = min(results, key=lambda x: (x['distance'], x['nodes']))
        path, distance, algo_name, nodes_explored = best_result['path'], best_result['distance'], best_result['name'], best_result['nodes']
    else:
        algo_map = { 
            'bfs': (bfs, 'BFS'), 'dfs': (dfs, 'DFS'), 
            'ucs': (ucs, 'UCS'), 'a_star': (a_star, 'A* Search') 
        }
        algo_func, algo_name = algo_map[algorithm]
        if algorithm == 'a_star':
            path, distance, nodes_explored = algo_func(campus_map, start, end, coordinates)
        else:
            path, distance, nodes_explored = algo_func(campus_map, start, end)

    if not path: return jsonify({'error': f'No path found using {algo_name}.'}), 404

    simplified_path = [loc for loc in path if not loc.startswith('J')]
    path_coords = [coordinates[loc] for loc in path]
    
    return jsonify({
        'path': ' -> '.join(simplified_path),
        'distance': round(distance, 2),
        'time': round(distance / 80, 2),
        'nodes_explored': nodes_explored,
        'path_coords': path_coords,
        'algorithm': algo_name
    })

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_query = data.get('question', '').lower().strip().replace('?', '')
    
    reset_commands = ['reset', 'clear', 'clear the map', 'clear selection', 'start over']
    if user_query in reset_commands:
        return jsonify({'action': 'reset'})

    # v-- PASTE YOUR GEMINI API KEY ON THIS LINE v--
    api_key = "AIzaSyDHR5IetXHLpv-EgRIWsumX_ga88lWqxxo"
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
    system_prompt = get_campus_context()
    payload = {"contents": [{"parts": [{"text": user_query}]}], "systemInstruction": {"parts": [{"text": system_prompt}]}}
    try:
        response = requests.post(api_url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        text_response = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
        
        if '{' in text_response and '}' in text_response:
            clean_text = text_response[text_response.find('{'):text_response.rfind('}')+1]
            try:
                command = json.loads(clean_text)
                if command.get('action') == 'navigate':
                    return jsonify(command)
            except json.JSONDecodeError:
                pass
            
        return jsonify({'answer': text_response or "Sorry, I couldn't process that."})
    except requests.exceptions.RequestException as e:
        print(f"LLM API Error: {e}")
        return jsonify({'answer': "Sorry, I'm having trouble connecting to my brain right now."}), 500

if __name__ == '__main__': app.run(debug=True)

