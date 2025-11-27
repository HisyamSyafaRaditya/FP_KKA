"""
2-OPT Local Search Optimization
Mengoptimasi urutan TPS dalam satu rute
"""

from typing import List, Dict
import copy
from src.graph import Graph


def two_opt_single_route(graph: Graph, route: List[str], 
                        improvement_threshold: float = 0.001,
                        max_iterations: int = 1000) -> List[str]:
    """
    Optimasi single route menggunakan 2-OPT
    
    Algoritma 2-OPT:
    1. Untuk setiap pasangan edge (i, i+1) dan (j, j+1) dimana i < j
    2. Hitung improvement jika ditukar
    3. Jika ada improvement, lakukan swap dan restart
    4. Ulangi sampai tidak ada improvement
    
    Args:
        graph: Graph object
        route: List node ID dalam rute (termasuk depot)
        improvement_threshold: Threshold untuk dianggap improvement
        max_iterations: Max iterasi untuk menghindari infinite loop
    
    Returns:
        Rute yang sudah dioptimasi
    """
    best_route = copy.deepcopy(route)
    improved = True
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route) - 1):
                # Hitung current distance
                current_dist = (graph.euclidean(best_route[i-1], best_route[i]) +
                              graph.euclidean(best_route[j], best_route[j+1]))
                
                # Hitung distance setelah swap
                new_dist = (graph.euclidean(best_route[i-1], best_route[j]) +
                          graph.euclidean(best_route[i], best_route[j+1]))
                
                # Check improvement
                if current_dist - new_dist > improvement_threshold:
                    # Reverse segment antara i dan j
                    best_route[i:j+1] = reversed(best_route[i:j+1])
                    improved = True
                    break
            
            if improved:
                break
    
    return best_route


def optimize_routes_2opt(graph: Graph, routes: Dict[str, List[str]],
                        improvement_threshold: float = 0.001,
                        max_iterations: int = 1000) -> Dict[str, List[str]]:
    """
    Optimasi semua rute menggunakan 2-OPT
    
    Args:
        graph: Graph object
        routes: Dict truck_id -> list node_id
        improvement_threshold: Threshold untuk improvement
        max_iterations: Max iterasi per rute
    
    Returns:
        Dict rute yang sudah dioptimasi
    """
    optimized_routes = {}
    
    for truck_id, route in routes.items():
        optimized_routes[truck_id] = two_opt_single_route(
            graph, route, improvement_threshold, max_iterations
        )
    
    return optimized_routes


def calculate_route_distance(graph: Graph, route: List[str]) -> float:
    """Hitung total jarak route"""
    if len(route) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(route) - 1):
        total_distance += graph.euclidean(route[i], route[i+1])
    
    return total_distance


def calculate_total_distance(graph: Graph, routes: Dict[str, List[str]]) -> float:
    """Hitung total jarak semua rute"""
    total = 0.0
    for route in routes.values():
        total += calculate_route_distance(graph, route)
    return total
