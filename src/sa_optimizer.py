"""
Simulated Annealing Global Optimization
Mengoptimasi penempatan TPS antar truk dan dalam truk
"""

import random
import math
import copy
from typing import Dict, List, Tuple
from src.graph import Graph
from src.two_opt import calculate_route_distance, calculate_total_distance


def get_all_tps_from_routes(routes: Dict[str, List[str]], depot_id: str) -> List[str]:
    """Extract semua TPS node dari routes"""
    all_tps = []
    for route in routes.values():
        for node_id in route:
            if node_id != depot_id:
                all_tps.append(node_id)
    return all_tps


def create_route_from_tps_order(tps_order: List[str], depot_id: str) -> List[str]:
    """Create route dari urutan TPS"""
    return [depot_id] + tps_order + [depot_id]


def routes_to_tps_order(routes: Dict[str, List[str]], depot_id: str) -> Tuple[List[str], List[Tuple[int, int]]]:
    """
    Convert routes menjadi urutan TPS dan route indices
    
    Returns:
        (flattened_tps_order, route_indices)
        route_indices: list (start, end) index untuk setiap rute
    """
    all_tps = []
    route_indices = []
    
    for truck_id in sorted(routes.keys()):
        route = routes[truck_id]
        start_idx = len(all_tps)
        
        # Tambahkan TPS (skip depot)
        for node_id in route:
            if node_id != depot_id:
                all_tps.append(node_id)
        
        end_idx = len(all_tps)
        route_indices.append((start_idx, end_idx))
    
    return all_tps, route_indices


def tps_order_to_routes(tps_order: List[str], route_indices: List[Tuple[int, int]], 
                       truck_ids: List[str], depot_id: str) -> Dict[str, List[str]]:
    """Convert urutan TPS kembali menjadi routes"""
    routes = {}
    
    for truck_id, (start_idx, end_idx) in zip(truck_ids, route_indices):
        tps_segment = tps_order[start_idx:end_idx]
        routes[truck_id] = [depot_id] + tps_segment + [depot_id]
    
    return routes


def generate_neighbor_solution(routes: Dict[str, List[str]], depot_id: str) -> Dict[str, List[str]]:
    """
    Generate neighbor solution dari current solution
    
    Operasi:
    1. Swap dua TPS dalam rute yang sama (50% probability)
    2. Swap TPS antara dua rute berbeda (50% probability)
    """
    new_routes = copy.deepcopy(routes)
    truck_ids = sorted(new_routes.keys())
    
    tps_order, route_indices = routes_to_tps_order(new_routes, depot_id)
    
    if random.random() < 0.5 and len(tps_order) >= 2:
        # Swap dalam rute
        idx1 = random.randint(0, len(tps_order) - 1)
        idx2 = random.randint(0, len(tps_order) - 1)
        if idx1 != idx2:
            tps_order[idx1], tps_order[idx2] = tps_order[idx2], tps_order[idx1]
    else:
        # Swap antar rute (pindah satu TPS ke rute lain)
        if len(tps_order) >= 2:
            idx = random.randint(0, len(tps_order) - 1)
            new_pos = random.randint(0, len(tps_order) - 1)
            
            if idx != new_pos:
                tps_node = tps_order.pop(idx)
                tps_order.insert(new_pos, tps_node)
    
    new_routes = tps_order_to_routes(tps_order, route_indices, truck_ids, depot_id)
    return new_routes


def simulated_annealing_optimize(graph: Graph, routes: Dict[str, List[str]], 
                                depot_id: str,
                                t0: float = 100.0,
                                cooling_rate: float = 0.995,
                                iter_per_temp: int = 200,
                                t_min: float = 0.1) -> Dict[str, List[str]]:
    """
    Simulated Annealing untuk global optimization
    
    Args:
        graph: Graph object
        routes: Initial routes
        depot_id: ID node depot
        t0: Initial temperature
        cooling_rate: Cooling rate per iteration
        iter_per_temp: Jumlah iterasi per temperature
        t_min: Minimum temperature (stop condition)
    
    Returns:
        Optimized routes
    """
    current_routes = copy.deepcopy(routes)
    best_routes = copy.deepcopy(routes)
    
    current_cost = calculate_total_distance(graph, current_routes)
    best_cost = current_cost
    
    temperature = t0
    
    while temperature > t_min:
        for _ in range(iter_per_temp):
            # Generate neighbor
            neighbor_routes = generate_neighbor_solution(current_routes, depot_id)
            neighbor_cost = calculate_total_distance(graph, neighbor_routes)
            
            # Acceptance probability
            delta = neighbor_cost - current_cost
            
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_routes = neighbor_routes
                current_cost = neighbor_cost
                
                # Update best jika lebih baik
                if current_cost < best_cost:
                    best_routes = copy.deepcopy(current_routes)
                    best_cost = current_cost
        
        # Cool down
        temperature *= cooling_rate
    
    return best_routes


def optimize_routes_sa(graph: Graph, routes: Dict[str, List[str]], depot_id: str,
                      t0: float = 100.0, cooling_rate: float = 0.995,
                      iter_per_temp: int = 200, t_min: float = 0.1) -> Dict[str, List[str]]:
    """Wrapper untuk SA optimization"""
    return simulated_annealing_optimize(
        graph, routes, depot_id,
        t0=t0, cooling_rate=cooling_rate,
        iter_per_temp=iter_per_temp, t_min=t_min
    )
