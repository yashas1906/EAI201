from queue import PriorityQueue
print("Helping the rat to escape the underground pipes")
print("Through Uniform Cost Search (UCS)\n")
def ucs(graph, start, target):
    
    priority_queue = PriorityQueue()
    priority_queue.put((0, start))  
    
    came_from = {start: None}
    cost_so_far = {start: 0}
    visited = set() 

    while not priority_queue.empty():
        current_cost, current_node = priority_queue.get()
        
        visited.add(current_node) 

        if current_node == target:
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = came_from.get(current_node)
            path.reverse()
            return path, cost_so_far[target], visited 

        for neighbor, edge_cost in graph.get(current_node, []):
            new_cost = cost_so_far[current_node] + edge_cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority_queue.put((new_cost, neighbor))
                came_from[neighbor] = current_node

    return None, float('inf'), visited 

if __name__ == "__main__":
    graph = {
        'A': [('B', 1), ('C', 4)],
        'B': [('A', 1), ('C', 10), ('D', 2), ('E', 5)],
        'C': [('A', 4), ('F', 3)],
        'D': [('B', 2)],
        'E': [('B', 5), ('F', 1)],
        'F': [('C', 3), ('E', 1)]
    }
    start_node = 'A'
    target_node = 'F'
    path, cost, junctions_explored = ucs(graph, start_node, target_node)
    if path:
        print("Path Found")
        print("Path Followed:", " -> ".join(path))
        print("Total Cost of Path:", cost)
        print("Total Junctions in Path:", len(path))
        print("Total Junctions Explored by UCS:", len(junctions_explored))
        
    else:
        print("No path could be found")