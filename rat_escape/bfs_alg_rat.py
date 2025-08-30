from collections import deque 

print("Helping the rat to escape the underground pipes")
print("Through Breadth-First Search (BFS)\n")

def bfs_find_path(graph, start_junction, target_junction):
    queue = deque([[start_junction]])
    visited = {start_junction}
    while queue:
        
        path = queue.popleft()
        node = path[-1]

        
        if node == target_junction:
            return path, visited 

    
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    

    return None, visited

if __name__ == "__main__":
    
    graph = {
        'A' : ['B', 'C'],
        'B' : ['A', 'D', 'E'],
        'C' : ['A', 'F'],
        'D' : ['B'],
        'E' : ['B', 'F'],
        'F' : ['C', 'E']
    }

    start_node = 'A'
    target_node = 'F'
    final_path, junctions_visited_during_search = bfs_find_path(graph, start_node, target_node)
    if final_path:
        print("Path Found")
        print("Path Followed:", " -> ".join(final_path))
        path_cost = len(final_path) - 1
        print("Total Cost of Path (pipes traveled):", path_cost)
        print("Total Junctions in Path:", len(final_path))
        print("Total Junctions Explored by BFS:", len(junctions_visited_during_search))
    else:
        print("No path could be found.")