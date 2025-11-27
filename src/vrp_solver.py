"""
VRP Solver Wrapper
Mengkombinasikan berbagai algoritma optimization
"""

from typing import Dict, List, Tuple
from src.graph import Graph
from src.astar import astar, compute_path_distance
from src.two_opt import optimize_routes_2opt, calculate_total_distance
from src.sa_optimizer import optimize_routes_sa


class VRPSolver:
    """Wrapper untuk VRP solving dengan berbagai metode"""
    
    def __init__(self, graph: Graph, depot_id: str):
        self.graph = graph
        self.depot_id = depot_id
    
    def compute_full_paths(self, routes: Dict[str, List[str]]) -> Dict[str, List[List[str]]]:
        """
        Compute full paths dengan A* untuk setiap segment
        
        Args:
            routes: Dict truck_id -> list node_id (TPS nodes)
        
        Returns:
            Dict truck_id -> list of paths (setiap path adalah list node_id)
        """
        full_paths = {}
        
        for truck_id, route in routes.items():
            truck_paths = []
            
            # Hitung path antar consecutive nodes dalam route
            for i in range(len(route) - 1):
                start = route[i]
                end = route[i + 1]
                
                # A* pathfinding
                path = astar(self.graph, start, end)
                if path is None:
                    path = [start, end]  # Fallback ke direct connection
                
                truck_paths.append(path)
            
            full_paths[truck_id] = truck_paths
        
        return full_paths
    
    def compute_full_paths_as_single_list(self, routes: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Compute full paths dan return sebagai single list per truck
        
        Args:
            routes: Dict truck_id -> list node_id
        
        Returns:
            Dict truck_id -> list node_id (full path)
        """
        full_paths_dict = self.compute_full_paths(routes)
        result = {}
        
        for truck_id, paths in full_paths_dict.items():
            # Flatten paths dengan menghindari duplikasi di junctions
            full_path = []
            for i, path in enumerate(paths):
                if i == 0:
                    full_path.extend(path)
                else:
                    # Skip first node karena same dengan last node dari previous path
                    full_path.extend(path[1:])
            
            result[truck_id] = full_path
        
        return result
    
    def optimize_routes_2opt(self, routes: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Optimasi routes menggunakan 2-OPT
        
        Args:
            routes: Dict truck_id -> list node_id
        
        Returns:
            Optimized routes
        """
        return optimize_routes_2opt(self.graph, routes)
    
    def optimize_routes_sa(self, routes: Dict[str, List[str]],
                          t0: float = 100.0, cooling_rate: float = 0.995,
                          iter_per_temp: int = 200, t_min: float = 0.1) -> Dict[str, List[str]]:
        """
        Optimasi routes menggunakan Simulated Annealing
        
        Args:
            routes: Dict truck_id -> list node_id
            t0: Initial temperature
            cooling_rate: Cooling rate
            iter_per_temp: Iterations per temperature
            t_min: Minimum temperature
        
        Returns:
            Optimized routes
        """
        return optimize_routes_sa(
            self.graph, routes, self.depot_id,
            t0=t0, cooling_rate=cooling_rate,
            iter_per_temp=iter_per_temp, t_min=t_min
        )
    
    def evaluate_routes(self, full_paths: Dict[str, List[str]]) -> Dict:
        """
        Evaluate routes (compute distances dan metrics)
        
        Args:
            full_paths: Dict truck_id -> list node_id (full paths)
        
        Returns:
            Dict dengan metrics:
            - total_distance: total jarak semua truk
            - distances_per_truck: dict truck_id -> distance
            - num_trucks: jumlah truk
            - num_stops: total jumlah stops
        """
        distances_per_truck = {}
        total_distance = 0.0
        total_stops = 0
        
        for truck_id, path in full_paths.items():
            distance = compute_path_distance(self.graph, path)
            distances_per_truck[truck_id] = distance
            total_distance += distance
            total_stops += len(path) - 2  # Exclude start dan end depot
        
        return {
            'total_distance': total_distance,
            'distances_per_truck': distances_per_truck,
            'num_trucks': len(full_paths),
            'num_stops': total_stops
        }
    
    def evaluate_routes_simple(self, routes: Dict[str, List[str]]) -> Dict:
        """
        Evaluate routes dengan jarak langsung (Euclidean)
        
        Args:
            routes: Dict truck_id -> list node_id
        
        Returns:
            Dict dengan metrics
        """
        distances_per_truck = {}
        total_distance = 0.0
        total_stops = 0
        
        for truck_id, route in routes.items():
            distance = 0.0
            for i in range(len(route) - 1):
                distance += self.graph.euclidean(route[i], route[i+1])
            
            distances_per_truck[truck_id] = distance
            total_distance += distance
            total_stops += len([n for n in route if n != self.depot_id])
        
        return {
            'total_distance': total_distance,
            'distances_per_truck': distances_per_truck,
            'num_trucks': len(routes),
            'num_stops': total_stops
        }
