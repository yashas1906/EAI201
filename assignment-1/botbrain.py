import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import math

# --- CAMPUS DATA AND GRAPH MODEL ---

class CampusNavigator:
    def __init__(self):
        self.graph = {}
        self.locations = {}
        self._setup_graph()

    def _add_edge(self, u, v, weight):
        """Adds a bidirectional edge to the graph."""
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []
        self.graph[u].append((v, weight))
        self.graph[v].append((u, weight))

    def _setup_graph(self):
        """Initializes the campus map with locations, coordinates, and paths."""
        # Coordinates for drawing on the Tkinter canvas (heuristic for A*)
        self.locations = {
            'Main Gate': (200, 600),
            'Auditorium': (200, 550),
            'Library': (300, 550),
            'Cafe': (100, 500),
            'Academic Block B': (200, 450),
            'Faculty Hostel': (350, 400),
            'Laundry': (250, 350),
            'Food Court': (150, 350),
            'Hostel': (400, 300),
            'Sports Complex': (150, 150),
            'Football Ground': (50, 100),
            'Cricket Ground': (100, 50),
            'Basketball Court': (200, 50),
            'Volleyball Court': (250, 80),
            'Tennis Court': (300, 100)
        }

        edges = [
            ('Main Gate', 'Auditorium', 90),
            ('Main Gate', 'Library', 105),
            ('Main Gate', 'Cafe', 125),
            ('Auditorium', 'Library', 12),
            ('Auditorium', 'Academic Block B', 115),
            ('Library', 'Academic Block B', 160),
            ('Cafe', 'Academic Block B', 148),
            ('Academic Block B', 'Faculty Hostel', 165),
            ('Academic Block B', 'Laundry', 182),
            ('Academic Block B', 'Food Court', 183),
            ('Faculty Hostel', 'Laundry', 82),
            ('Faculty Hostel', 'Hostel', 30), # Note: Project doc has 30 and 280, using 30 as more likely
            ('Laundry', 'Food Court', 105),
            ('Food Court', 'Sports Complex', 667),
            ('Hostel', 'Laundry', 268),
            ('Hostel', 'Sports Complex', 500),
            ('Hostel', 'Library', 635),
            ('Sports Complex', 'Football Ground', 154),
            ('Sports Complex', 'Cricket Ground', 43),
            ('Sports Complex', 'Basketball Court', 29),
            ('Sports Complex', 'Volleyball Court', 72),
            ('Sports Complex', 'Tennis Court', 82)
        ]

        for u, v, w in edges:
            self._add_edge(u, v, w)

    # --- SEARCH ALGORITHMS ---

    def _heuristic(self, a, b):
        """Calculate Euclidean distance as the heuristic for A*."""
        (x1, y1) = self.locations[a]
        (x2, y2) = self.locations[b]
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def bfs(self, start, end):
        """Breadth-First Search"""
        queue = [(start, [start])]
        visited = {start}
        while queue:
            current, path = queue.pop(0)
            if current == end:
                return self._calculate_path_details(path)
            
            # Sort neighbors to ensure consistent path discovery (optional)
            sorted_neighbors = sorted(self.graph.get(current, []), key=lambda x: x[0])

            for neighbor, _ in sorted_neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path))
        return None, 0, 0

    def dfs(self, start, end):
        """Depth-First Search"""
        stack = [(start, [start])]
        visited = {start}
        while stack:
            current, path = stack.pop()
            if current == end:
                return self._calculate_path_details(path)
            
            # Sort neighbors to ensure consistent path discovery (optional, reverse for typical stack behavior)
            sorted_neighbors = sorted(self.graph.get(current, []), key=lambda x: x[0], reverse=True)

            for neighbor, _ in sorted_neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    stack.append((neighbor, new_path))
        return None, 0, 0

    def ucs(self, start, end):
        """Uniform Cost Search (Dijkstra's)"""
        priority_queue = [(0, start, [start])]
        visited = set()
        while priority_queue:
            cost, current, path = heapq.heappop(priority_queue)
            if current in visited:
                continue
            visited.add(current)
            if current == end:
                return self._calculate_path_details(path)

            for neighbor, weight in self.graph.get(current, []):
                if neighbor not in visited:
                    new_cost = cost + weight
                    new_path = list(path)
                    new_path.append(neighbor)
                    heapq.heappush(priority_queue, (new_cost, neighbor, new_path))
        return None, 0, 0
        
    def a_star(self, start, end):
        """A* Search"""
        priority_queue = [(0, start, [start])] # (f_cost, node, path)
        g_costs = {location: float('inf') for location in self.locations}
        g_costs[start] = 0
        
        while priority_queue:
            _, current, path = heapq.heappop(priority_queue)

            if current == end:
                return self._calculate_path_details(path)

            for neighbor, weight in self.graph.get(current, []):
                tentative_g_cost = g_costs[current] + weight
                if tentative_g_cost < g_costs[neighbor]:
                    g_costs[neighbor] = tentative_g_cost
                    f_cost = tentative_g_cost + self._heuristic(neighbor, end)
                    new_path = list(path)
                    new_path.append(neighbor)
                    heapq.heappush(priority_queue, (f_cost, neighbor, new_path))
        return None, 0, 0
        
    def _calculate_path_details(self, path):
        """Calculates total distance and time for a given path."""
        distance = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            # Find the weight of the edge between u and v
            edge_weight = next((weight for neighbor, weight in self.graph[u] if neighbor == v), 0)
            distance += edge_weight
        
        time = distance / 1.4 / 60  # in minutes
        return path, distance, time

# --- GUI APPLICATION ---

class App(tk.Tk):
    def __init__(self, navigator):
        super().__init__()
        self.navigator = navigator
        self.title("BotBrain - Chanakya University Navigator")
        self.geometry("1200x800")
        
        # --- UI Elements ---
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Map Canvas
        self.canvas = tk.Canvas(self.main_frame, bg="lightgrey")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Controls Frame
        self.controls_frame = ttk.Frame(self.main_frame, width=300)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.controls_frame.pack_propagate(False)

        # Title
        ttk.Label(self.controls_frame, text="BotBrain Navigator", font=("Helvetica", 18, "bold")).pack(pady=10)

        # Location Selection
        location_names = sorted(list(self.navigator.locations.keys()))
        self.start_var = tk.StringVar(value=location_names[0])
        self.end_var = tk.StringVar(value=location_names[1])

        ttk.Label(self.controls_frame, text="Start Location:").pack(pady=(10, 2))
        ttk.Combobox(self.controls_frame, textvariable=self.start_var, values=location_names, state="readonly").pack(fill=tk.X, padx=10)

        ttk.Label(self.controls_frame, text="Destination:").pack(pady=(10, 2))
        ttk.Combobox(self.controls_frame, textvariable=self.end_var, values=location_names, state="readonly").pack(fill=tk.X, padx=10)

        # Algorithm Selection
        ttk.Label(self.controls_frame, text="Algorithm:").pack(pady=(20, 5))
        self.algo_var = tk.StringVar(value="UCS")
        algos = [("Breadth-First Search", "BFS"), ("Depth-First Search", "DFS"),
                 ("Uniform Cost Search", "UCS"), ("A* Search", "A_STAR")]
        for text, val in algos:
            ttk.Radiobutton(self.controls_frame, text=text, variable=self.algo_var, value=val).pack(anchor=tk.W, padx=10)

        # Find Route Button
        ttk.Button(self.controls_frame, text="Find Route", command=self.find_route).pack(pady=20, fill=tk.X, padx=10)
        
        # Results Display
        self.results_frame = ttk.LabelFrame(self.controls_frame, text="Route Information")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.path_label = ttk.Label(self.results_frame, text="Path: ", wraplength=280, justify=tk.LEFT)
        self.path_label.pack(pady=5, padx=5, anchor=tk.W)
        self.dist_label = ttk.Label(self.results_frame, text="Total Distance: ")
        self.dist_label.pack(pady=5, padx=5, anchor=tk.W)
        self.time_label = ttk.Label(self.results_frame, text="Estimated Time: ")
        self.time_label.pack(pady=5, padx=5, anchor=tk.W)

        # Bind canvas resize event
        self.canvas.bind("<Configure>", self.draw_map)

    def draw_map(self, event=None, highlight_path=None):
        """Draws the campus map on the canvas."""
        self.canvas.delete("all")
        
        # Draw edges
        for u, connections in self.navigator.graph.items():
            for v, _ in connections:
                x1, y1 = self.navigator.locations[u]
                x2, y2 = self.navigator.locations[v]
                self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=1.5)

        # Draw highlighted path
        if highlight_path:
            for i in range(len(highlight_path) - 1):
                u, v = highlight_path[i], highlight_path[i+1]
                x1, y1 = self.navigator.locations[u]
                x2, y2 = self.navigator.locations[v]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=4)

        # Draw nodes (locations)
        for name, (x, y) in self.navigator.locations.items():
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="skyblue", outline="black")
            self.canvas.create_text(x, y - 12, text=name, font=("Helvetica", 8))

    def find_route(self):
        start = self.start_var.get()
        end = self.end_var.get()
        algo = self.algo_var.get()

        if start == end:
            messagebox.showinfo("Info", "Start and destination locations cannot be the same.")
            return

        path_finders = {
            "BFS": self.navigator.bfs,
            "DFS": self.navigator.dfs,
            "UCS": self.navigator.ucs,
            "A_STAR": self.navigator.a_star
        }

        path, distance, time = path_finders[algo](start, end)
        
        if path:
            self.draw_map(highlight_path=path)
            self.path_label.config(text=f"Path: {' -> '.join(path)}")
            self.dist_label.config(text=f"Total Distance: {distance:.2f} meters")
            self.time_label.config(text=f"Estimated Time: {time:.2f} minutes")
        else:
            self.draw_map()
            messagebox.showerror("Error", f"No path found from {start} to {end}.")
            self.path_label.config(text="Path: Not found")
            self.dist_label.config(text="Total Distance: N/A")
            self.time_label.config(text="Estimated Time: N/A")


if __name__ == "__main__":
    campus_nav = CampusNavigator()
    app = App(campus_nav)
    app.mainloop()
