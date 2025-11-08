#!/usr/bin/env python3
"""
BotBrain - Chanakya University Campus Navigator
A sophisticated desktop GUI application for campus navigation with multiple pathfinding algorithms.

Required Dependencies:
pip install tkintermapview Pillow googlemaps

Note: You need to replace 'YOUR_API_KEY_HERE' with a valid Google Maps API key
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkintermapview
import googlemaps
import math
from collections import deque, defaultdict
import heapq
import threading
import re

# Google Maps API Key - REPLACE WITH YOUR ACTUAL API KEY
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"

# Campus Data
locations = {
    'Main Gate': {'lat': 13.2300, 'lng': 77.7050, 'info': "Main entrance and security checkpoint."},
    'Auditorium': {'lat': 13.2305, 'lng': 77.7052, 'info': "Main hall for events and lectures."},
    'Library': {'lat': 13.2306, 'lng': 77.7058, 'info': "Library: Open 8 AM - 10 PM."},
    'Cafe': {'lat': 13.2312, 'lng': 77.7048, 'info': "Campus Cafe: Open 9 AM - 6 PM."},
    'Academic Block B': {'lat': 13.2315, 'lng': 77.7055, 'info': "Classrooms and faculty offices."},
    'Faculty Hostel': {'lat': 13.2320, 'lng': 77.7065, 'info': "Residence for faculty members."},
    'Laundry': {'lat': 13.2325, 'lng': 77.7060, 'info': "Student laundry services."},
    'Food Court': {'lat': 13.2328, 'lng': 77.7055, 'info': "Main dining area for students."},
    'Hostel': {'lat': 13.2325, 'lng': 77.7075, 'info': "Student residential building."},
    'Sports Complex': {'lat': 13.2340, 'lng': 77.7040, 'info': "Indoor and outdoor sports facilities."},
    'Football Ground': {'lat': 13.2345, 'lng': 77.7035, 'info': "Full-sized football field."},
    'Cricket Ground': {'lat': 13.2348, 'lng': 77.7042, 'info': "Practice nets and cricket pitch."},
    'Basketball Court': {'lat': 13.2342, 'lng': 77.7045, 'info': "Outdoor basketball court."},
    'Volleyball Court': {'lat': 13.2338, 'lng': 77.7046, 'info': "Outdoor volleyball court."},
    'Tennis Court': {'lat': 13.2335, 'lng': 77.7048, 'info': "Campus tennis courts."}
}

edges = [
    ('Main Gate', 'Auditorium', 90), ('Main Gate', 'Library', 105), ('Main Gate', 'Cafe', 125),
    ('Auditorium', 'Library', 12), ('Auditorium', 'Academic Block B', 115),
    ('Library', 'Academic Block B', 160), ('Cafe', 'Academic Block B', 148),
    ('Academic Block B', 'Faculty Hostel', 165), ('Academic Block B', 'Laundry', 182),
    ('Academic Block B', 'Food Court', 183), ('Faculty Hostel', 'Laundry', 82),
    ('Faculty Hostel', 'Hostel', 30), ('Laundry', 'Food Court', 105),
    ('Food Court', 'Sports Complex', 667), ('Hostel', 'Laundry', 268),
    ('Hostel', 'Sports Complex', 500), ('Hostel', 'Library', 635),
    ('Sports Complex', 'Football Ground', 154), ('Sports Complex', 'Cricket Ground', 43),
    ('Sports Complex', 'Basketball Court', 29), ('Sports Complex', 'Volleyball Court', 72),
    ('Sports Complex', 'Tennis Court', 82)
]

class PathfindingAlgorithms:
    """Implementation of various pathfinding algorithms"""
    
    def __init__(self, locations, edges):
        self.locations = locations
        self.graph = self._build_graph(edges)
    
    def _build_graph(self, edges):
        """Build adjacency list from edges"""
        graph = defaultdict(list)
        for start, end, weight in edges:
            graph[start].append((end, weight))
            graph[end].append((start, weight))
        return graph
    
    def haversine_distance(self, loc1, loc2):
        """Calculate haversine distance between two locations (in meters)"""
        lat1, lng1 = self.locations[loc1]['lat'], self.locations[loc1]['lng']
        lat2, lng2 = self.locations[loc2]['lat'], self.locations[loc2]['lng']
        
        R = 6371000  # Earth radius in meters
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def bfs(self, start, goal):
        """Breadth-First Search"""
        if start == goal:
            return [start], 0
        
        queue = deque([(start, [start], 0)])
        visited = set([start])
        
        while queue:
            current, path, distance = queue.popleft()
            
            for neighbor, weight in self.graph[current]:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    new_distance = distance + weight
                    
                    if neighbor == goal:
                        return new_path, new_distance
                    
                    visited.add(neighbor)
                    queue.append((neighbor, new_path, new_distance))
        
        return None, 0
    
    def dfs(self, start, goal):
        """Depth-First Search"""
        if start == goal:
            return [start], 0
        
        def dfs_recursive(current, path, distance, visited):
            if current == goal:
                return path, distance
            
            visited.add(current)
            
            for neighbor, weight in self.graph[current]:
                if neighbor not in visited:
                    result = dfs_recursive(neighbor, path + [neighbor], 
                                         distance + weight, visited.copy())
                    if result[0]:
                        return result
            
            return None, 0
        
        return dfs_recursive(start, [start], 0, set())
    
    def ucs(self, start, goal):
        """Uniform Cost Search"""
        if start == goal:
            return [start], 0
        
        heap = [(0, start, [start])]
        visited = set()
        
        while heap:
            distance, current, path = heapq.heappop(heap)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == goal:
                return path, distance
            
            for neighbor, weight in self.graph[current]:
                if neighbor not in visited:
                    new_distance = distance + weight
                    new_path = path + [neighbor]
                    heapq.heappush(heap, (new_distance, neighbor, new_path))
        
        return None, 0
    
    def a_star(self, start, goal):
        """A* Search Algorithm"""
        if start == goal:
            return [start], 0
        
        heap = [(0, start, [start], 0)]
        visited = set()
        
        while heap:
            f_score, current, path, g_score = heapq.heappop(heap)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == goal:
                return path, g_score
            
            for neighbor, weight in self.graph[current]:
                if neighbor not in visited:
                    new_g_score = g_score + weight
                    h_score = self.haversine_distance(neighbor, goal)
                    f_score = new_g_score + h_score
                    new_path = path + [neighbor]
                    heapq.heappush(heap, (f_score, neighbor, new_path, new_g_score))
        
        return None, 0

class ChatbotWindow:
    """Chatbot interface for natural language commands"""
    
    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("BotBrain Chat Assistant")
        self.window.geometry("500x600")
        self.window.resizable(True, True)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.window, wrap=tk.WORD, height=25, state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = ttk.Frame(self.window)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_message)
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.RIGHT)
        
        # Welcome message
        self.add_message("Bot", "Hello! I'm your campus navigation assistant. Try commands like:\n" +
                        "• 'route from Library to Cafe'\n" +
                        "• 'where is Sports Complex'\n" +
                        "• 'info for Auditorium'")
    
    def add_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self, event=None):
        """Process user message"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        self.add_message("You", message)
        self.input_entry.delete(0, tk.END)
        
        # Process command
        response = self.process_command(message.lower())
        self.add_message("Bot", response)
    
    def process_command(self, command):
        """Parse and execute chat commands"""
        # Route command
        route_match = re.search(r'route from (.+?) to (.+?)(?:\s|$)', command)
        if route_match:
            start_loc = self.find_location(route_match.group(1).strip())
            end_loc = self.find_location(route_match.group(2).strip())
            
            if start_loc and end_loc:
                self.main_app.start_var.set(start_loc)
                self.main_app.dest_var.set(end_loc)
                self.main_app.find_route()
                return f"Finding route from {start_loc} to {end_loc}..."
            else:
                return "I couldn't find one or both of those locations. Please check the spelling."
        
        # Where is command
        where_match = re.search(r'where is (.+?)(?:\s|$)', command)
        if where_match:
            location = self.find_location(where_match.group(1).strip())
            if location:
                self.main_app.pan_to_location(location)
                return f"Showing {location} on the map."
            else:
                return "I couldn't find that location. Please check the spelling."
        
        # Info command
        info_match = re.search(r'info for (.+?)(?:\s|$)', command)
        if info_match:
            location = self.find_location(info_match.group(1).strip())
            if location:
                info = locations[location]['info']
                return f"{location}: {info}"
            else:
                return "I couldn't find that location. Please check the spelling."
        
        return "I didn't understand that command. Try 'route from X to Y', 'where is X', or 'info for X'."
    
    def find_location(self, query):
        """Find location by partial name match"""
        query = query.lower()
        for location in locations.keys():
            if query in location.lower():
                return location
        return None

class BotBrainApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("BotBrain - Chanakya University Navigator")
        self.root.geometry("1200x800")
        
        # Initialize pathfinding algorithms
        self.pathfinder = PathfindingAlgorithms(locations, edges)
        
        # Initialize Google Maps client
        if GOOGLE_MAPS_AVAILABLE:
            try:
                self.gmaps = googlemaps.Client(key=GOOGLE_API_KEY) if GOOGLE_API_KEY != "YOUR_API_KEY_HERE" else None
            except:
                self.gmaps = None
        else:
            self.gmaps = None
        
        # UI Variables
        self.start_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.algorithm_var = tk.StringVar(value="A* Search")
        
        # Current route visualization
        self.current_route = None
        
        self.setup_ui()
        self.setup_map()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Map frame (left side)
        map_frame = ttk.Frame(main_frame)
        map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Control panel (right side)
        control_frame = ttk.LabelFrame(main_frame, text="Navigation Control", padding=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Map widget
        self.map_widget = tkintermapview.TkinterMapView(
            map_frame, width=800, height=600, corner_radius=0
        )
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        
        # Location selection
        ttk.Label(control_frame, text="Start Location:").pack(anchor=tk.W, pady=(0, 5))
        start_combo = ttk.Combobox(control_frame, textvariable=self.start_var, 
                                  values=list(locations.keys()), width=25)
        start_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Destination:").pack(anchor=tk.W, pady=(0, 5))
        dest_combo = ttk.Combobox(control_frame, textvariable=self.dest_var,
                                 values=list(locations.keys()), width=25)
        dest_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Algorithm selection
        ttk.Label(control_frame, text="Algorithm:").pack(anchor=tk.W, pady=(10, 5))
        algorithms = ["BFS", "DFS", "UCS", "A* Search", "Google Maps"]
        for algo in algorithms:
            ttk.Radiobutton(control_frame, text=algo, variable=self.algorithm_var,
                           value=algo).pack(anchor=tk.W)
        
        # Find route button
        ttk.Button(control_frame, text="Find Route", 
                  command=self.find_route).pack(fill=tk.X, pady=(20, 10))
        
        # Chat button
        ttk.Button(control_frame, text="Open Chat Assistant", 
                  command=self.open_chat).pack(fill=tk.X, pady=(0, 20))
        
        # Results display
        results_frame = ttk.LabelFrame(control_frame, text="Route Information", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=30)
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_map(self):
        """Setup the map widget and markers"""
        # Set map position to Chanakya University
        self.map_widget.set_position(13.23, 77.70)
        self.map_widget.set_zoom(16)
        
        # Add markers for all locations
        self.markers = {}
        for name, data in locations.items():
            marker = self.map_widget.set_marker(
                data['lat'], data['lng'], text=name,
                command=lambda m=name: self.marker_clicked(m)
            )
            self.markers[name] = marker
    
    def marker_clicked(self, location_name):
        """Handle marker click events"""
        info = locations[location_name]['info']
        messagebox.showinfo(f"Location: {location_name}", info)
    
    def pan_to_location(self, location):
        """Pan map to specific location"""
        if location in locations:
            data = locations[location]
            self.map_widget.set_position(data['lat'], data['lng'])
            self.map_widget.set_zoom(18)
    
    def find_route(self):
        """Find and display route using selected algorithm"""
        start = self.start_var.get()
        dest = self.dest_var.get()
        algorithm = self.algorithm_var.get()
        
        if not start or not dest:
            messagebox.showerror("Error", "Please select both start and destination.")
            return
        
        if start == dest:
            messagebox.showinfo("Info", "Start and destination are the same!")
            return
        
        # Clear previous route
        if self.current_route:
            self.map_widget.delete(self.current_route)
            self.current_route = None
        
        # Find route based on selected algorithm
        if algorithm == "Google Maps":
            self.find_google_route(start, dest)
        else:
            self.find_algorithmic_route(start, dest, algorithm)
    
    def find_algorithmic_route(self, start, dest, algorithm):
        """Find route using custom algorithms"""
        try:
            # Get path using selected algorithm
            if algorithm == "BFS":
                path, distance = self.pathfinder.bfs(start, dest)
            elif algorithm == "DFS":
                path, distance = self.pathfinder.dfs(start, dest)
            elif algorithm == "UCS":
                path, distance = self.pathfinder.ucs(start, dest)
            elif algorithm == "A* Search":
                path, distance = self.pathfinder.a_star(start, dest)
            
            if not path:
                self.display_results("No route found!", "", "")
                return
            
            # Calculate walking time (assuming 1.4 m/s walking speed)
            walking_time = int(distance / 1.4)
            minutes = walking_time // 60
            seconds = walking_time % 60
            time_str = f"{minutes}m {seconds}s"
            
            # Display results
            path_str = " → ".join(path)
            self.display_results(f"Algorithm: {algorithm}", 
                               f"Path: {path_str}",
                               f"Distance: {distance:.0f}m",
                               f"Est. Time: {time_str}")
            
            # Visualize route on map
            self.visualize_route(path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Route finding failed: {str(e)}")
    
    def find_google_route(self, start, dest):
        """Find route using Google Maps API"""
        if not self.gmaps:
            messagebox.showerror("Error", "Google Maps API not configured. Please set your API key.")
            return
        
        def google_route_thread():
            try:
                start_coords = (locations[start]['lat'], locations[start]['lng'])
                dest_coords = (locations[dest]['lat'], locations[dest]['lng'])
                
                # Get directions
                directions = self.gmaps.directions(
                    start_coords, dest_coords, mode="walking"
                )
                
                if not directions:
                    self.root.after(0, lambda: self.display_results("No Google route found!", "", ""))
                    return
                
                route = directions[0]
                leg = route['legs'][0]
                distance = leg['distance']['text']
                duration = leg['duration']['text']
                
                # Get polyline points for visualization
                polyline = route['overview_polyline']['points']
                path_coords = self.decode_polyline(polyline)
                
                # Display results
                self.root.after(0, lambda: self.display_results(
                    "Algorithm: Google Maps (Live)",
                    f"Route: {start} → {dest}",
                    f"Distance: {distance}",
                    f"Duration: {duration}"
                ))
                
                # Visualize route
                self.root.after(0, lambda: self.visualize_google_route(path_coords))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Google route failed: {str(e)}"))
        
        # Run in separate thread to avoid UI blocking
        threading.Thread(target=google_route_thread, daemon=True).start()
    
    def decode_polyline(self, polyline_str):
        """Decode Google's polyline format to coordinates"""
        coords = []
        index = 0
        lat = 0
        lng = 0
        
        while index < len(polyline_str):
            # Decode latitude
            b = 0
            shift = 0
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                lat += (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            
            dlat = ~(lat >> 1) if lat & 1 else (lat >> 1)
            lat = dlat
            
            # Decode longitude  
            b = 0
            shift = 0
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                lng += (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            
            dlng = ~(lng >> 1) if lng & 1 else (lng >> 1)
            lng = dlng
            
            coords.append((lat / 1e5, lng / 1e5))
        
        return coords
    
    def visualize_route(self, path):
        """Visualize algorithmic route on map"""
        if len(path) < 2:
            return
        
        # Create coordinate pairs for the path
        coords = []
        for location in path:
            data = locations[location]
            coords.append((data['lat'], data['lng']))
        
        # Draw path on map
        self.current_route = self.map_widget.set_path(coords, color="blue", width=5)
    
    def visualize_google_route(self, coords):
        """Visualize Google Maps route on map"""
        if len(coords) < 2:
            return
        
        # Draw detailed path on map
        self.current_route = self.map_widget.set_path(coords, color="red", width=4)
    
    def display_results(self, *lines):
        """Display route results in the text widget"""
        self.results_text.delete(1.0, tk.END)
        for line in lines:
            if line:
                self.results_text.insert(tk.END, line + "\n")
    
    def open_chat(self):
        """Open the chatbot window"""
        ChatbotWindow(self.root, self)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = BotBrainApp(root)
    
    # Handle window closing
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()