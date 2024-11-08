class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, i):
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x != root_y:
            if self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            elif self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1

def greedy_edge_selection_tsp_general_graph(edges, n):
    """
    Greedy edge selection algorithm for TSP in a general graph.

    Parameters:
    - edges: List of tuples (weight, u, v) where u and v are vertices connected by an edge with the given weight.
    - n: Number of vertices in the graph.

    Returns:
    - path: List of vertices representing the TSP path.
    - edge_list: List of edges in the form (u, v) representing the TSP path.
    - total_distance: The total weight of the TSP path.
    """
    # Sort edges by their weight
    edges.sort(key=lambda x: x[0])
    
    uf = UnionFind(n)
    degree = [0] * n
    edge_list = []
    total_distance = 0

    # Add edges to the edge list while avoiding cycles and connectivity
    weight, u, v = edges[0]
    uf.union(u, v)
    edge_list.append((u, v))
    total_distance += weight
    degree[u] += 1
    degree[v] += 1
    
    for i in range(n):
        for weight, u, v in edges:
            #Add and edge if it's does not form a cycle and is connected the main path
            if uf.find(u) != uf.find(v) and (degree[u] == 1 or degree[v] == 1):  
                uf.union(u, v)
                edge_list.append((u, v))
                total_distance += weight
                degree[u] += 1
                degree[v] += 1
                break
    
    start_index = degree.index(1)
    # Reconstruct the path from the edge list
    path = reconstruct_path(edge_list, n, start_index)

    return path

def reconstruct_path(edge_list, n, start):
    """
    Reconstructs the path from the list of edges.

    Parameters:
    - edge_list: List of edges in the form (u, v) representing the TSP path.
    - n: Number of vertices in the graph.

    Returns:
    - path: List of vertices in the order they are visited.
    """
    # Create an adjacency list
    adj = {i: [] for i in range(n)}
    for u, v in edge_list:
        adj[u].append(v)
        adj[v].append(u)

    # Start from any vertex (e.g., vertex 0)
    start_vertex = start
    path = [start_vertex]
    current_vertex = start_vertex

    # Trace the path using the adjacency list
    while len(path) < n:
        for neighbor in adj[current_vertex]:
            if neighbor not in path:
                path.append(neighbor)
                current_vertex = neighbor
                break
        else:
            break

    return path

if __name__ == "__main__":
    # Example usage with a general graph
    edges = [
        (2, 0, 1),  # Edge with weight 2 between vertex 0 and 1
        (3, 0, 2),  # Edge with weight 3 between vertex 0 and 2
        (1, 1, 2),  # Edge with weight 1 between vertex 1 and 2
        (4, 1, 3),  # Edge with weight 4 between vertex 1 and 3
        (5, 2, 3),  # Edge with weight 5 between vertex 2 and 3
    ]

    n = 4  # Number of vertices

    path = greedy_edge_selection_tsp_general_graph(edges, n)

    print("Path:", path)
