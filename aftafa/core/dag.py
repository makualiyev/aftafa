from collections import defaultdict
from typing import List


class Graph:
    """
    A directed graph data structure using adjacency lists.
    
    Attributes:
    -----------
    graph: dict
        A dictionary that maps each node to a list of its adjacent nodes.
    in_degree: dict
        A dictionary that maps each node to its in-degree.
    """

    def __init__(self) -> None:
        """
        Initializes a new empty graph.
        """
        self.graph = defaultdict(list)
        self.in_degree = defaultdict(int)


    def add_edge(self, u: int, v: int) -> bool:
        """
        Adds a directed edge from node u to node v.

        Parameters:
        -----------
        u:  int
            The starting node of the edge.
        v:  int
            The ending node of the edge.

        Returns:
        --------
        bool
            True if the edge is added successfully, False if the edge would create a cycle.
        """
        if u == v or v in self.graph[u]:
            return  # Edge already exists or creates a cycle
        
        self.graph[u].append(v)
        cycle_exists = self.detect_cycle()
        if cycle_exists:
            # If a cycle is detected, remove the edge and return False
            self.graph[u].remove(v)
            return False
        
        # If no cycle is detected, add the edge and update in-degree
        self.graph[u].append(v)
        self.in_degree[v] += 1
        return True
    
    def detect_cycle(self) -> bool:
        """
        Detects cycles in the graph using a depth-first search algorithm.

        Returns:
        --------
        bool
            True if a cycle exists, False otherwise.
        """
        visited = set()

        def dfs(node, stack=None):
            stack = set() if stack is None else stack

            visited.add(node)
            stack.add(node)

            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor, stack):
                        return True
                elif neighbor in stack:
                    return True
            
            stack.remove(node)
            return False
        
        for node in list(self.graph):
            if node not in visited:
                if dfs(node):
                    return True
                
        return False
        