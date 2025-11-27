"""
Simulator dan Visualization
Menampilkan rute truk sampah dalam format visual
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Set, Tuple
from src.graph import Graph


class Simulator:
    """Simulator untuk visualisasi rute"""
    
    def __init__(self, graph: Graph, depot_id: str):
        self.graph = graph
        self.depot_id = depot_id
        self.colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 
                      'pink', 'gray', 'olive', 'cyan', 'magenta', 'yellow']
    
    def visualize_routes(self, routes: Dict[str, List[str]], tps_ids: Set[str],
                        title: str = "Garbage Truck Routes",
                        output_file: str = None, figsize: Tuple = (14, 10)):
        """
        Visualisasi rute dalam plot
        
        Args:
            routes: Dict truck_id -> list node_id
            tps_ids: Set dari TPS node IDs
            title: Judul plot
            output_file: Path untuk save gambar (jika None, tidak disave)
            figsize: Ukuran figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot semua edges graph (light gray)
        for edge in self.graph.edges:
            node1_id, node2_id = edge
            node1 = self.graph.get_node(node1_id)
            node2 = self.graph.get_node(node2_id)
            
            ax.plot([node1.x, node2.x], [node1.y, node2.y], 'lightgray', linewidth=0.5, zorder=1)
        
        # Plot semua nodes (light)
        for node_id, node in self.graph.nodes.items():
            if node_id == self.depot_id:
                continue
            if node_id in tps_ids:
                continue
            
            ax.plot(node.x, node.y, 'o', color='lightblue', markersize=3, zorder=2)
        
        # Plot routes dengan warna berbeda
        for truck_idx, (truck_id, route) in enumerate(sorted(routes.items())):
            color = self.colors[truck_idx % len(self.colors)]
            
            # Plot path
            route_nodes = [self.graph.get_node(node_id) for node_id in route]
            xs = [n.x for n in route_nodes]
            ys = [n.y for n in route_nodes]
            
            ax.plot(xs, ys, 'o-', color=color, linewidth=2, markersize=6, 
                   label=f'Truck {truck_id}', zorder=3, alpha=0.7)
        
        # Plot TPS (orange squares)
        for tps_id in tps_ids:
            node = self.graph.get_node(tps_id)
            rect = patches.Rectangle((node.x - 0.15, node.y - 0.15), 0.3, 0.3,
                                    linewidth=1, edgecolor='orange', facecolor='orange',
                                    zorder=4, alpha=0.6)
            ax.add_patch(rect)
        
        # Plot depot (large red star)
        depot_node = self.graph.get_node(self.depot_id)
        ax.plot(depot_node.x, depot_node.y, '*', color='red', markersize=20, 
               label='Depot', zorder=5)
        
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"Visualization saved to {output_file}")
        
        return fig, ax
    
    def visualize_full_paths(self, full_paths: Dict[str, List[str]], tps_ids: Set[str],
                            title: str = "Full Routes with A* Paths",
                            output_file: str = None, figsize: Tuple = (14, 10)):
        """
        Visualisasi full paths dengan A* detailing
        
        Args:
            full_paths: Dict truck_id -> list node_id (full path)
            tps_ids: Set dari TPS node IDs
            title: Judul plot
            output_file: Path untuk save gambar
            figsize: Ukuran figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot semua edges graph
        for edge in self.graph.edges:
            node1_id, node2_id = edge
            node1 = self.graph.get_node(node1_id)
            node2 = self.graph.get_node(node2_id)
            
            ax.plot([node1.x, node2.x], [node1.y, node2.y], 'lightgray', linewidth=0.5, zorder=1)
        
        # Plot semua nodes
        for node_id, node in self.graph.nodes.items():
            if node_id == self.depot_id:
                continue
            if node_id in tps_ids:
                continue
            
            ax.plot(node.x, node.y, 'o', color='lightblue', markersize=2, zorder=2)
        
        # Plot full paths
        for truck_idx, (truck_id, path) in enumerate(sorted(full_paths.items())):
            color = self.colors[truck_idx % len(self.colors)]
            
            path_nodes = [self.graph.get_node(node_id) for node_id in path]
            xs = [n.x for n in path_nodes]
            ys = [n.y for n in path_nodes]
            
            ax.plot(xs, ys, '-', color=color, linewidth=1.5, 
                   label=f'Truck {truck_id}', zorder=3, alpha=0.6)
            
            # Mark waypoints
            ax.plot(xs, ys, 'o', color=color, markersize=3, zorder=3, alpha=0.5)
        
        # Plot TPS
        for tps_id in tps_ids:
            node = self.graph.get_node(tps_id)
            rect = patches.Rectangle((node.x - 0.15, node.y - 0.15), 0.3, 0.3,
                                    linewidth=1, edgecolor='orange', facecolor='orange',
                                    zorder=4, alpha=0.7)
            ax.add_patch(rect)
        
        # Plot depot
        depot_node = self.graph.get_node(self.depot_id)
        ax.plot(depot_node.x, depot_node.y, '*', color='red', markersize=20, 
               label='Depot', zorder=5)
        
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"Visualization saved to {output_file}")
        
        return fig, ax


def visualize_comparison(graph: Graph, depot_id: str, tps_ids: Set[str],
                        routes_initial: Dict[str, List[str]],
                        routes_2opt: Dict[str, List[str]],
                        routes_sa: Dict[str, List[str]],
                        output_file: str = None, figsize: Tuple = (18, 6)):
    """
    Visualisasi perbandingan antara initial, 2opt, dan SA
    
    Args:
        graph: Graph object
        depot_id: ID node depot
        tps_ids: Set dari TPS node IDs
        routes_initial: Initial routes
        routes_2opt: Routes setelah 2-OPT
        routes_sa: Routes setelah SA
        output_file: Path untuk save gambar
        figsize: Ukuran figure
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    
    configs = [
        (routes_initial, axes[0], "Initial Greedy Solution"),
        (routes_2opt, axes[1], "After 2-OPT Optimization"),
        (routes_sa, axes[2], "After Simulated Annealing"),
    ]
    
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 
             'pink', 'gray', 'olive', 'cyan', 'magenta', 'yellow']
    
    for routes, ax, title in configs:
        # Plot edges
        for edge in graph.edges:
            node1_id, node2_id = edge
            node1 = graph.get_node(node1_id)
            node2 = graph.get_node(node2_id)
            ax.plot([node1.x, node2.x], [node1.y, node2.y], 'lightgray', linewidth=0.5, zorder=1)
        
        # Plot nodes
        for node_id, node in graph.nodes.items():
            if node_id == depot_id or node_id in tps_ids:
                continue
            ax.plot(node.x, node.y, 'o', color='lightblue', markersize=2, zorder=2)
        
        # Plot routes
        for truck_idx, (truck_id, route) in enumerate(sorted(routes.items())):
            color = colors[truck_idx % len(colors)]
            route_nodes = [graph.get_node(node_id) for node_id in route]
            xs = [n.x for n in route_nodes]
            ys = [n.y for n in route_nodes]
            ax.plot(xs, ys, 'o-', color=color, linewidth=2, markersize=4, alpha=0.7, zorder=3)
        
        # Plot TPS
        for tps_id in tps_ids:
            node = graph.get_node(tps_id)
            rect = patches.Rectangle((node.x - 0.15, node.y - 0.15), 0.3, 0.3,
                                    linewidth=1, edgecolor='orange', facecolor='orange',
                                    zorder=4, alpha=0.6)
            ax.add_patch(rect)
        
        # Plot depot
        depot_node = graph.get_node(depot_id)
        ax.plot(depot_node.x, depot_node.y, '*', color='red', markersize=20, zorder=5)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"Comparison visualization saved to {output_file}")
    
    return fig
