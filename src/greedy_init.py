"""
Greedy Initial VRP Solution Generator
Menghasilkan solusi awal untuk Vehicle Routing Problem
"""

from typing import List, Dict, Tuple
from src.graph import Graph


class TPS:
    """Temporary Disposal Site"""
    def __init__(self, tps_id: str, node_id: str, demand: float):
        self.id = tps_id
        self.node_id = node_id
        self.demand = demand
    
    def __repr__(self):
        return f"TPS({self.id}, node={self.node_id}, demand={self.demand})"


class Truck:
    """Vehicle/Truck dalam VRP"""
    def __init__(self, truck_id: str, capacity: float):
        self.id = truck_id
        self.capacity = capacity
    
    def __repr__(self):
        return f"Truck({self.id}, capacity={self.capacity})"


def greedy_initial_solution(graph: Graph, tps_list: List[TPS], 
                           depot_id: str, trucks: List[Truck]) -> Dict[str, List[str]]:
    """
    Generate rute awal menggunakan greedy algorithm
    
    Algoritma:
    1. Untuk setiap truk (dalam urutan)
    2. Mulai dari depot
    3. Pilih TPS terdekat yang belum dikunjungi dan masih muat kapasitas
    4. Update kapasitas truk
    5. Ulangi sampai tidak ada TPS yang bisa ditambah atau kapasitas penuh
    6. Kembali ke depot
    
    Args:
        graph: Graph object
        tps_list: List TPS dengan demand
        depot_id: ID node depot
        trucks: List truck dengan capacity
    
    Returns:
        Dict dengan key=truck_id, value=list TPS node_id (tidak termasuk depot di awal)
    """
    routes: Dict[str, List[str]] = {truck.id: [] for truck in trucks}
    remaining_tps = set(tps.node_id for tps in tps_list)
    tps_dict = {tps.node_id: tps for tps in tps_list}
    
    # Gunakan kapasitas tersisa untuk setiap truk
    truck_remaining_capacity = {truck.id: truck.capacity for truck in trucks}
    
    for truck in trucks:
        current_location = depot_id
        current_capacity = truck_remaining_capacity[truck.id]
        
        while remaining_tps:
            # Cari TPS terdekat yang masih muat
            best_tps_node = None
            best_distance = float('inf')
            
            for tps_node_id in remaining_tps:
                tps = tps_dict[tps_node_id]
                
                # Check jika demand masih muat
                if tps.demand > current_capacity:
                    continue
                
                # Hitung jarak dari lokasi sekarang ke TPS
                distance = graph.euclidean(current_location, tps_node_id)
                
                if distance < best_distance:
                    best_distance = distance
                    best_tps_node = tps_node_id
            
            if best_tps_node is None:
                # Tidak ada TPS yang bisa ditambah
                break
            
            # Tambahkan TPS ke rute
            routes[truck.id].append(best_tps_node)
            tps_obj = tps_dict[best_tps_node]
            
            # Update
            current_location = best_tps_node
            current_capacity -= tps_obj.demand
            remaining_tps.remove(best_tps_node)
    
    # Jika masih ada TPS yang belum dialokasikan, tambahkan ke first available truck
    if remaining_tps:
        for tps_node_id in remaining_tps:
            tps = tps_dict[tps_node_id]
            # Cari truck dengan kapasitas cukup
            for truck in trucks:
                if truck_remaining_capacity[truck.id] >= tps.demand:
                    routes[truck.id].append(tps_node_id)
                    truck_remaining_capacity[truck.id] -= tps.demand
                    break
    
    return routes


def format_routes_with_depot(routes: Dict[str, List[str]], 
                            depot_id: str) -> Dict[str, List[str]]:
    """
    Format rute untuk output: tambahkan depot di awal dan akhir
    
    Args:
        routes: Dict dari greedy_initial_solution
        depot_id: ID node depot
    
    Returns:
        Dict dengan depot di awal dan akhir setiap rute
    """
    formatted = {}
    for truck_id, tps_nodes in routes.items():
        formatted[truck_id] = [depot_id] + tps_nodes + [depot_id]
    return formatted
