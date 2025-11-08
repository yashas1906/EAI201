import heapq

# Import campus data from the database file
from database import campus_map, coordinates, building_info, faq_data

def bfs(graph, start, goal):
    """
    Breadth-First Search algorithm to find the shortest path in terms of number of edges.
    """
    if start not in graph or goal not in graph:
        return None, float('inf'), 0
        
    visited = set()
    queue = [(start, [start])]
    nodes_explored = 0

    while queue:
        nodes_explored += 1
        current, path = queue.pop(0)

        if current == goal:
            total_distance = 0
            for i in range(len(path) - 1):
                total_distance += graph[path[i]][path[i+1]]
            return path, total_distance, nodes_explored
        
        if current not in visited:
            visited.add(current)
            for neighbor, distance in graph[current].items():
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path))
    
    return None, float('inf'), nodes_explored

def dfs(graph, start, goal):
    """
    Depth-First Search algorithm to find a path between two nodes.
    """
    if start not in graph or goal not in graph:
        return None, float('inf'), 0

    visited = set()
    stack = [(start, [start])]
    nodes_explored = 0
    
    while stack:
        nodes_explored += 1
        current, path = stack.pop()
        
        if current == goal:
            total_distance = 0
            for i in range(len(path) - 1):
                total_distance += graph[path[i]][path[i+1]]
            return path, total_distance, nodes_explored

        if current not in visited:
            visited.add(current)
            for neighbor, distance in graph[current].items():
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    stack.append((neighbor, new_path))

    return None, float('inf'), nodes_explored

def ucs(graph, start, goal):
    """
    Uniform Cost Search algorithm to find the path with the lowest cumulative distance.
    """
    if start not in graph or goal not in graph:
        return None, float('inf'), 0

    visited = set()
    priority_queue = [(0, start, [start])]
    nodes_explored = 0

    while priority_queue:
        nodes_explored += 1
        cost, current, path = heapq.heappop(priority_queue)

        if current == goal:
            return path, cost, nodes_explored
        
        if current not in visited:
            visited.add(current)
            for neighbor, distance in graph[current].items():
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    heapq.heappush(priority_queue, (cost + distance, neighbor, new_path))
    
    return None, float('inf'), nodes_explored

def a_star(graph, start, goal, coordinates):
    """
    A* Search algorithm to find the most efficient path using a heuristic.
    """
    def heuristic(node1, node2):
        x1, y1 = coordinates[node1]
        x2, y2 = coordinates[node2]
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    
    if start not in graph or goal not in graph:
        return None, float('inf'), 0

    visited = set()
    priority_queue = [(0 + heuristic(start, goal), 0, start, [start])]
    nodes_explored = 0
    
    while priority_queue:
        nodes_explored += 1
        _, cost, current, path = heapq.heappop(priority_queue)

        if current == goal:
            return path, cost, nodes_explored
        
        if current not in visited:
            visited.add(current)
            for neighbor, distance in graph[current].items():
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    new_cost = cost + distance
                    heapq.heappush(priority_queue, (new_cost + heuristic(neighbor, goal), new_cost, neighbor, new_path))
    
    return None, float('inf'), nodes_explored


def main():
    """
    Main function to run the campus navigator.
    """
    print("Welcome to the BotBrain Campus Navigator for Chanakya University!")

    while True:
        print("\nAvailable locations:")
        for location in campus_map.keys():
            print(f"- {location}")

        start_node = input("\nEnter your starting location: ")
        if start_node not in campus_map:
            print("Invalid starting location. Please try again.")
            continue
            
        goal_node = input("Enter your destination: ")
        if goal_node not in campus_map:
            print("Invalid destination. Please try again.")
            continue

        print("\nChoose a search algorithm:")
        print("1. Breadth-First Search (BFS)")
        print("2. Depth-First Search (DFS)")
        print("3. Uniform Cost Search (UCS)")
        print("4. A* Search")
        
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            path, distance, nodes_explored = bfs(campus_map, start_node, goal_node)
            algorithm = "Breadth-First Search"
        elif choice == '2':
            path, distance, nodes_explored = dfs(campus_map, start_node, goal_node)
            algorithm = "Depth-First Search"
        elif choice == '3':
            path, distance, nodes_explored = ucs(campus_map, start_node, goal_node)
            algorithm = "Uniform Cost Search"
        elif choice == '4':
            path, distance, nodes_explored = a_star(campus_map, start_node, goal_node, coordinates)
            algorithm = "A* Search"
        else:
            print("Invalid choice. Please try again.")
            continue

        if path:
            print(f"\n--- {algorithm} Results ---")
            print(f"Path: {' -> '.join(path)}")
            print(f"Total distance: {distance} meters")
            print(f"Estimated walking time: {distance / 80:.2f} minutes")
            print(f"Nodes explored: {nodes_explored}")
        else:
            print(f"\nNo path found from {start_node} to {goal_node}.")

        # Ask if the user wants to find another path or get building info
        while True:
            sub_choice = input("\nWhat would you like to do next?\n1. Find another path\n2. Get information about a location\n3. Ask a question (FAQ)\n4. Exit\nEnter your choice (1-4): ")
            if sub_choice == '1':
                break
            elif sub_choice == '2':
                location_info = input("Enter the location you want to know about: ")
                if location_info in building_info:
                    print(f"\n--- Information for {location_info} ---")
                    for key, value in building_info[location_info].items():
                        print(f"{key}: {value}")
                else:
                    print("Invalid location.")
            elif sub_choice == '3':
                question = input("What is your question? ").lower()
                answer = faq_data.get(question, "Sorry, I don't have an answer for that.")
                print(f"BotBrain: {answer}")
            elif sub_choice == '4':
                print("Thank you for using BotBrain!")
                return
            else:
                print("Invalid choice. Please try again.")
        if sub_choice == '1':
            continue

if __name__ == "__main__":
    main()

