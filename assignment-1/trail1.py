import tkinter as tk
from tkinter import ttk, messagebox
from math import sqrt
import heapq

# --- DATA (from database.py) ---
# To make this a standalone application, the data is included directly.
campus_map = {
    'Main Gate': {'Admin Block': 90, 'Cafe': 152, 'Library': 105},
    'Admin Block': {'Main Gate': 90, 'Auditorium': 12, 'Library': 12, 'Academic Block B': 115},
    'Cafe': {'Main Gate': 152, 'Auditorium': 12, 'Academic Block B': 148},
    'Library': {'Main Gate': 105, 'Admin Block': 12, 'Hostel': 635},
    'Auditorium': {'Admin Block': 12, 'Cafe': 12},
    'Academic Block B': {'Admin Block': 115, 'Cafe': 148, 'Food Court': 183, 'Faculty Hostel': 165},
    'Food Court': {'Academic Block B': 183, 'Laundry': 105, 'Sports Complex': 667},
    'Laundry': {'Food Court': 105, 'Faculty Hostel': 82, 'Hostel': 268},
    'Faculty Hostel': {'Academic Block B': 165, 'Laundry': 82, 'Hostel': 280},
    'Hostel': {'Library': 635, 'Laundry': 268, 'Faculty Hostel': 280, 'Sports Complex': 590},
    'Sports Complex': {'Food Court': 667, 'Hostel': 590, 'Football Ground': 154, 'Cricket Ground': 43, 'Basketball Court': 72, 'Volleyball Court': 83, 'Tennis Court': 82},
    'Football Ground': {'Sports Complex': 154},
    'Cricket Ground': {'Sports Complex': 43},
    'Basketball Court': {'Sports Complex': 72},
    'Volleyball Court': {'Sports Complex': 83},
    'Tennis Court': {'Sports Complex': 82},
}

# Coordinates for drawing on a 2D canvas (and for A* heuristic)
# These are scaled for display purposes.
coordinates = {
    'Main Gate': (250, 560), 'Admin Block': (250, 480), 'Cafe': (150, 480),
    'Library': (350, 480), 'Auditorium': (200, 450), 'Academic Block B': (250, 380),
    'Food Court': (250, 280), 'Laundry': (320, 250), 'Faculty Hostel': (350, 350),
    'Hostel': (450, 300), 'Sports Complex': (350, 150), 'Football Ground': (250, 100),
    'Cricket Ground': (300, 50), 'Basketball Court': (380, 50), 'Volleyball Court': (430, 80),
    'Tennis Court': (450, 120)
}

faq_data = {
    "what are the library hours?": "The Library is open from 9 am to 5 pm.",
    "when does the cafe close?": "The Cafe closes at 5 pm.",
    "what are the timings for the sports complex?": "The Sports Complex is open from 6 am to 7:30 pm.",
    "when is the food court open?": "The Food Court is open from 7:30 am to 9:30 pm.",
    "what time does the admin block open?": "The Admin Block opens at 9 am.",
    "what is the hostel in-time?": "The hostel in-time is 10 pm.",
    "when can i use the laundry services?": "Laundry services are available from 9:30 am to 6 pm.",
    "where can i pay my fees?": "You can pay your fees at the Admin Block.",
    "what is in academic block b?": "Academic Block B is the Engineering block.",
    "how do i use the navigator?": "Select a start and destination, choose an algorithm, and click 'Find Path'.",
    "how do i connect to the campus wi-fi?": "Connect using your student credentials. For help, visit the IT department in the Admin Block."
}

# --- SEARCH ALGORITHMS ---
def bfs(graph, start, goal):
    if start not in graph or goal not in graph: return None, float('inf'), 0
    visited, queue, nodes_explored = set(), [(start, [start])], 0
    while queue:
        nodes_explored += 1
        current, path = queue.pop(0)
        if current == goal:
            dist = sum(graph[path[i]][path[i+1]] for i in range(len(path) - 1))
            return path, dist, nodes_explored
        if current not in visited:
            visited.add(current)
            for neighbor in graph.get(current, {}):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
    return None, float('inf'), nodes_explored

def dfs(graph, start, goal):
    if start not in graph or goal not in graph: return None, float('inf'), 0
    visited, stack, nodes_explored = set(), [(start, [start])], 0
    while stack:
        nodes_explored += 1
        current, path = stack.pop()
        if current == goal:
            dist = sum(graph[path[i]][path[i+1]] for i in range(len(path) - 1))
            return path, dist, nodes_explored
        if current not in visited:
            visited.add(current)
            for neighbor in reversed(list(graph.get(current, {}))):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))
    return None, float('inf'), nodes_explored

def ucs(graph, start, goal):
    if start not in graph or goal not in graph: return None, float('inf'), 0
    visited, pq, nodes_explored = set(), [(0, start, [start])], 0
    while pq:
        nodes_explored += 1
        cost, current, path = heapq.heappop(pq)
        if current == goal: return path, cost, nodes_explored
        if current not in visited:
            visited.add(current)
            for neighbor, weight in graph.get(current, {}).items():
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor, path + [neighbor]))
    return None, float('inf'), nodes_explored

def a_star(graph, start, goal, coords):
    def heuristic(n1, n2):
        x1, y1 = coords[n1]
        x2, y2 = coords[n2]
        return sqrt((x1 - x2)**2 + (y1 - y2)**2)

    if start not in graph or goal not in graph: return None, float('inf'), 0
    visited, pq, nodes_explored = set(), [(0 + heuristic(start, goal), 0, start, [start])], 0
    while pq:
        nodes_explored += 1
        _, cost, current, path = heapq.heappop(pq)
        if current == goal: return path, cost, nodes_explored
        if current not in visited:
            visited.add(current)
            for neighbor, weight in graph.get(current, {}).items():
                if neighbor not in visited:
                    new_cost = cost + weight
                    priority = new_cost + heuristic(neighbor, goal)
                    heapq.heappush(pq, (priority, new_cost, neighbor, path + [neighbor]))
    return None, float('inf'), nodes_explored

# --- GUI APPLICATION ---
class CampusNavigatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BotBrain: Campus Navigator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f2f5')

        # --- Main Layout ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(main_frame, width=400, padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Left Panel Widgets ---
        self._create_controls(left_panel)
        self._create_results_display(left_panel)
        self._create_chatbot(left_panel)

        # --- Right Panel Widgets ---
        self.map_canvas = tk.Canvas(right_panel, bg="white", highlightthickness=0)
        self.map_canvas.pack(fill=tk.BOTH, expand=True)
        self.map_canvas.bind("<Configure>", lambda e: self.draw_map())

    def _create_controls(self, parent):
        controls_frame = ttk.LabelFrame(parent, text="Find a Path", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        locations = sorted(list(campus_map.keys()))
        
        ttk.Label(controls_frame, text="Start Location:").pack(fill=tk.X, pady=2)
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(controls_frame, textvariable=self.start_var, values=locations, state='readonly')
        self.start_combo.pack(fill=tk.X, pady=2, ipady=4)
        self.start_combo.set(locations[0])

        ttk.Label(controls_frame, text="Destination:").pack(fill=tk.X, pady=2)
        self.goal_var = tk.StringVar()
        self.goal_combo = ttk.Combobox(controls_frame, textvariable=self.goal_var, values=locations, state='readonly')
        self.goal_combo.pack(fill=tk.X, pady=2, ipady=4)
        self.goal_combo.set(locations[-1])

        ttk.Label(controls_frame, text="Algorithm:").pack(fill=tk.X, pady=(10, 2))
        self.algo_var = tk.StringVar(value="A*")
        algo_frame = ttk.Frame(controls_frame)
        algo_frame.pack(fill=tk.X)
        algos = ["BFS", "DFS", "UCS", "A*"]
        for algo in algos:
            rb = ttk.Radiobutton(algo_frame, text=algo, variable=self.algo_var, value=algo)
            rb.pack(side=tk.LEFT, padx=5, expand=True)
        
        find_btn = ttk.Button(controls_frame, text="Find Path", command=self.find_path, style="Accent.TButton")
        find_btn.pack(fill=tk.X, pady=(10, 0), ipady=5)
        
        # Style for the button
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#4f46e5")


    def _create_results_display(self, parent):
        self.results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        self.results_frame.pack(fill=tk.X, pady=10)
        self.results_label = ttk.Label(self.results_frame, text="Select locations and an algorithm to see the results.", wraplength=350)
        self.results_label.pack(fill=tk.X)

    def _create_chatbot(self, parent):
        chat_frame = ttk.LabelFrame(parent, text="Ask BotBrain (FAQ)", padding="10")
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_history = tk.Text(chat_frame, wrap=tk.WORD, state='disabled', height=10, bg="#eef2ff", relief="solid", borderwidth=1)
        self.chat_history.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)
        self.chat_input = ttk.Entry(input_frame)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.chat_input.bind("<Return>", self.send_chat_message)
        chat_send_btn = ttk.Button(input_frame, text="Send", command=self.send_chat_message, style="Accent.TButton")
        chat_send_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.add_chat_message("Bot", "Hello! Ask a question, like 'what are the library hours?'")


    def find_path(self):
        start = self.start_var.get()
        goal = self.goal_var.get()
        algo = self.algo_var.get()

        if not start or not goal:
            messagebox.showerror("Error", "Please select both a start and goal location.")
            return

        if start == goal:
            messagebox.showinfo("Info", "Start and destination are the same.")
            self.results_label.config(text="Start and destination are the same.")
            self.draw_map() # Redraw map to clear previous path
            return

        path, dist, explored = None, 0, 0
        if algo == "BFS":
            path, dist, explored = bfs(campus_map, start, goal)
        elif algo == "DFS":
            path, dist, explored = dfs(campus_map, start, goal)
        elif algo == "UCS":
            path, dist, explored = ucs(campus_map, start, goal)
        elif algo == "A*":
            path, dist, explored = a_star(campus_map, start, goal, coordinates)

        if path:
            result_text = (
                f"Algorithm: {algo}\n"
                f"Path: {' -> '.join(path)}\n"
                f"Distance: {dist:.2f} meters\n"
                f"Walking Time: {dist/80:.2f} minutes\n"
                f"Nodes Explored: {explored}"
            )
            self.draw_map(path)
        else:
            result_text = f"No path found from {start} to {goal} using {algo}."
            self.draw_map()

        self.results_label.config(text=result_text)

    def draw_map(self, path=None):
        self.map_canvas.delete("all")
        
        # Draw edges (connections)
        for start_node, connections in campus_map.items():
            for end_node in connections:
                x1, y1 = coordinates[start_node]
                x2, y2 = coordinates[end_node]
                self.map_canvas.create_line(x1, y1, x2, y2, fill="#cccccc", width=1.5)

        # Draw nodes (locations)
        for name, (x, y) in coordinates.items():
            self.map_canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#4f46e5", outline="")
            self.map_canvas.create_text(x, y + 15, text=name, font=("Helvetica", 9), fill="#333333")

        # Draw the calculated path
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                x1, y1 = coordinates[path[i]]
                x2, y2 = coordinates[path[i+1]]
                self.map_canvas.create_line(x1, y1, x2, y2, fill="red", width=3, arrow=tk.LAST)


    def send_chat_message(self, event=None):
        user_msg = self.chat_input.get().strip()
        if not user_msg:
            return
        
        self.add_chat_message("You", user_msg)
        self.chat_input.delete(0, tk.END)

        # Get bot response
        bot_response = faq_data.get(user_msg.lower(), "Sorry, I don't have an answer for that.")
        self.add_chat_message("Bot", bot_response)

    def add_chat_message(self, sender, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = CampusNavigatorApp(root)
    root.mainloop()
