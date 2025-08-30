print("Helping the rat to escape the underground pipes")
print("Through Depth-First Search (DFS)\n")

def dfs(graph, start, goal):
    
    visited = set()
    stack = [start]
    came_from = {start: None}

    while stack:
        node = stack.pop()
        
        if node not in visited:
            visited.add(node)

            if node == goal:
                path = []
                while node is not None:
                    path.append(node)
                    node = came_from.get(node)
                path.reverse()
                return path, visited

            
            for neighbor in sorted(graph.get(node, []), reverse=True):
                if neighbor not in visited:
                    stack.append(neighbor)
                    came_from[neighbor] = node

    return None, visited

if __name__ == "__main__":
    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'F'],
        'D': ['B'],
        'E': ['B', 'F'],
        'F': ['C', 'E']
    }
    start_node = 'A'
    target_node = 'F'

    path, junctions_explored = dfs(graph, start_node, target_node)
    if path:
        print("Path Found")
        print("Path Followed:", " -> ".join(path))
        path_cost = len(path) - 1
        print("Total Cost of Path (pipes traveled):", path_cost)

        print("Total Junctions in Path:", len(path))
        print("Total Junctions Explored by DFS:", len(junctions_explored))
        
    else:
        print("No path could be found")