"""
Graph module untuk Garbage Truck Route Planner
Menangani representasi peta grid 2D dengan nodes dan edges
"""

import math
from typing import Dict, List, Tuple, Set


class Node:
    """Representasi node dalam graph"""
    def __init__(self, node_id: str, x: float, y: float):
        self.id = node_id
        self.x = x
        self.y = y
        self.neighbors: Dict[str, float] = {}  # {neighbor_id: distance}
    
    def __repr__(self):
        return f"Node({self.id}, ({self.x}, {self.y}))"


class Graph:
    """Graph berbasis grid untuk peta"""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Set[Tuple[str, str]] = set()
    
    def add_node(self, node_id: str, x: float, y: float) -> Node:
        """Tambah node ke graph"""
        node = Node(node_id, x, y)
        self.nodes[node_id] = node
        return node
    
    def add_edge(self, node_id1: str, node_id2: str, distance: float):
        """Tambah edge dua arah antara dua node"""
        if node_id1 not in self.nodes or node_id2 not in self.nodes:
            raise ValueError("Node tidak ditemukan")
        
        self.nodes[node_id1].neighbors[node_id2] = distance
        self.nodes[node_id2].neighbors[node_id1] = distance
        
        # Simpan edge sebagai tuple terurut untuk menghindari duplikasi
        edge = tuple(sorted([node_id1, node_id2]))
        self.edges.add(edge)
    
    def get_node(self, node_id: str) -> Node:
        """Ambil node dari graph"""
        return self.nodes.get(node_id)
    
    def euclidean(self, node_id1: str, node_id2: str) -> float:
        """Hitung jarak Euclidean antara dua node"""
        if node_id1 not in self.nodes or node_id2 not in self.nodes:
            return float('inf')
        
        node1 = self.nodes[node_id1]
        node2 = self.nodes[node_id2]
        
        dx = node1.x - node2.x
        dy = node1.y - node2.y
        return math.sqrt(dx * dx + dy * dy)
    
    def nearest_node_to_coord(self, x: float, y: float) -> str:
        """Cari node terdekat ke koordinat (x, y)"""
        if not self.nodes:
            return None
        
        min_distance = float('inf')
        nearest_id = None
        
        for node_id, node in self.nodes.items():
            dx = node.x - x
            dy = node.y - y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < min_distance:
                min_distance = distance
                nearest_id = node_id
        
        return nearest_id
    
    def load_from_grid(self, width: int, height: int, spacing: float = 1.0, 
                      obstacles: List[Tuple[int, int]] = None) -> None:
        """
        Load graph dari grid 2D
        
        Args:
            width: jumlah kolom
            height: jumlah baris
            spacing: jarak antar node
            obstacles: list koordinat grid yang diblokir (i, j)
        """
        if obstacles is None:
            obstacles = []
        
        obstacles_set = set(obstacles)
        
        # Buat nodes
        for i in range(height):
            for j in range(width):
                if (i, j) not in obstacles_set:
                    node_id = f"N{i}_{j}"
                    x = j * spacing
                    y = i * spacing
                    self.add_node(node_id, x, y)
        
        # Buat edges (4-directional: up, down, left, right)
        for i in range(height):
            for j in range(width):
                if (i, j) in obstacles_set:
                    continue
                
                current_id = f"N{i}_{j}"
                
                # Tetangga: up, down, left, right
                neighbors = [
                    (i-1, j),  # up
                    (i+1, j),  # down
                    (i, j-1),  # left
                    (i, j+1),  # right
                ]
                
                for ni, nj in neighbors:
                    if 0 <= ni < height and 0 <= nj < width:
                        if (ni, nj) not in obstacles_set:
                            neighbor_id = f"N{ni}_{nj}"
                            distance = spacing
                            self.add_edge(current_id, neighbor_id, distance)
    
    def get_all_nodes(self) -> List[Node]:
        """Ambil semua nodes"""
        return list(self.nodes.values())
    
    def get_neighbors(self, node_id: str) -> Dict[str, float]:
        """Ambil tetangga dari node"""
        if node_id not in self.nodes:
            return {}
        return self.nodes[node_id].neighbors.copy()
    
    def __repr__(self):
        return f"Graph(nodes={len(self.nodes)}, edges={len(self.edges)})"
