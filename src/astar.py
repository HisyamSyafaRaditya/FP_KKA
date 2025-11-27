"""
A* Algorithm untuk pathfinding
Digunakan untuk menemukan rute optimal antara dua node dalam graph
"""

import heapq
from typing import List, Dict, Tuple, Optional
from src.graph import Graph


def astar(graph: Graph, start_id: str, goal_id: str) -> Optional[List[str]]:
    """
    A* pathfinding algorithm
    
    Args:
        graph: Graph object
        start_id: ID node awal
        goal_id: ID node tujuan
    
    Returns:
        List node ID sebagai path dari start ke goal, atau None jika tidak ada path
    """
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return None
    
    if start_id == goal_id:
        return [start_id]
    
    # Priority queue: (f_score, counter, node_id)
    counter = 0
    open_set = [(0, counter, start_id)]
    counter += 1
    
    # g_score: cost dari start ke node
    g_score: Dict[str, float] = {start_id: 0}
    
    # f_score: g_score + heuristic
    f_score: Dict[str, float] = {start_id: graph.euclidean(start_id, goal_id)}
    
    # Untuk rekonstruksi path
    came_from: Dict[str, str] = {}
    
    # Set nodes yang sudah diproses
    closed_set = set()
    
    while open_set:
        current_f, _, current_id = heapq.heappop(open_set)
        
        if current_id in closed_set:
            continue
        
        closed_set.add(current_id)
        
        if current_id == goal_id:
            return reconstruct_path(came_from, current_id)
        
        # Check neighbors
        neighbors = graph.get_neighbors(current_id)
        
        for neighbor_id, distance in neighbors.items():
            if neighbor_id in closed_set:
                continue
            
            tentative_g = g_score[current_id] + distance
            
            # Jika neighbor belum ditemukan atau path baru lebih baik
            if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g
                f = tentative_g + graph.euclidean(neighbor_id, goal_id)
                f_score[neighbor_id] = f
                
                heapq.heappush(open_set, (f, counter, neighbor_id))
                counter += 1
    
    return None  # Tidak ada path ditemukan


def reconstruct_path(came_from: Dict[str, str], current_id: str) -> List[str]:
    """Rekonstruksi path dari came_from dictionary"""
    path = [current_id]
    
    while current_id in came_from:
        current_id = came_from[current_id]
        path.append(current_id)
    
    path.reverse()
    return path


def compute_path_distance(graph: Graph, path: List[str]) -> float:
    """Hitung total jarak dari path"""
    if len(path) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(path) - 1):
        total_distance += graph.euclidean(path[i], path[i+1])
    
    return total_distance
