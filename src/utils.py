"""
Utility Functions untuk I/O dan helpers
"""

import csv
import json
from typing import List, Dict
from src.graph import Graph
from src.greedy_init import TPS, Truck


def save_tps_to_csv(tps_list: List[TPS], output_file: str) -> None:
    """
    Simpan TPS list ke CSV file
    
    Format: id, node_id, demand
    
    Args:
        tps_list: List TPS objects
        output_file: Path output file
    """
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'node_id', 'demand'])
        
        for tps in tps_list:
            writer.writerow([tps.id, tps.node_id, tps.demand])
    
    print(f"TPS list saved to {output_file}")


def save_nodes_to_csv(graph: Graph, output_file: str) -> None:
    """
    Simpan node map ke CSV file
    
    Format: id, x, y, neighbors
    
    Args:
        graph: Graph object
        output_file: Path output file
    """
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'x', 'y', 'neighbors_count'])
        
        for node_id, node in sorted(graph.nodes.items()):
            neighbors_count = len(node.neighbors)
            writer.writerow([node_id, node.x, node.y, neighbors_count])
    
    print(f"Nodes map saved to {output_file}")


def save_routes_to_json(routes: Dict[str, List[str]], output_file: str) -> None:
    """
    Simpan routes ke JSON file
    
    Args:
        routes: Dict truck_id -> list node_id
        output_file: Path output file
    """
    with open(output_file, 'w') as f:
        json.dump(routes, f, indent=2)
    
    print(f"Routes saved to {output_file}")


def save_metrics_to_json(metrics: Dict, output_file: str) -> None:
    """
    Simpan metrics ke JSON file
    
    Args:
        metrics: Dict metrics
        output_file: Path output file
    """
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics saved to {output_file}")


def print_routes(routes: Dict[str, List[str]], title: str = "Routes") -> None:
    """
    Print routes ke console dengan format readable
    
    Args:
        routes: Dict truck_id -> list node_id
        title: Judul untuk print
    """
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    
    for truck_id, route in sorted(routes.items()):
        route_str = " -> ".join(route)
        print(f"Truck {truck_id}: {route_str}")
    
    print(f"{'='*60}\n")


def print_metrics(metrics: Dict, title: str = "Metrics") -> None:
    """
    Print metrics ke console
    
    Args:
        metrics: Dict metrics
        title: Judul untuk print
    """
    print(f"\n{title}")
    print(f"{'-'*40}")
    print(f"Total Distance: {metrics.get('total_distance', 0):.2f}")
    print(f"Number of Trucks: {metrics.get('num_trucks', 0)}")
    print(f"Total Stops: {metrics.get('num_stops', 0)}")
    
    distances_per_truck = metrics.get('distances_per_truck', {})
    if distances_per_truck:
        print(f"\nDistance per Truck:")
        for truck_id in sorted(distances_per_truck.keys()):
            dist = distances_per_truck[truck_id]
            print(f"  {truck_id}: {dist:.2f}")
    print()


def create_summary_report(metrics_initial: Dict, metrics_2opt: Dict, 
                         metrics_sa: Dict, output_file: str = None) -> str:
    """
    Create summary report dengan perbandingan semua metode
    
    Args:
        metrics_initial: Initial solution metrics
        metrics_2opt: 2-OPT metrics
        metrics_sa: SA metrics
        output_file: Path untuk save (optional)
    
    Returns:
        Report string
    """
    report = []
    report.append("="*70)
    report.append("GARBAGE TRUCK ROUTE PLANNER - OPTIMIZATION SUMMARY REPORT")
    report.append("="*70)
    report.append("")
    
    # Initial
    report.append("1. INITIAL GREEDY SOLUTION")
    report.append("-"*70)
    report.append(f"   Total Distance: {metrics_initial['total_distance']:.2f}")
    report.append(f"   Number of Trucks: {metrics_initial['num_trucks']}")
    report.append(f"   Total Stops: {metrics_initial['num_stops']}")
    report.append("")
    
    # 2-OPT
    improvement_2opt = ((metrics_initial['total_distance'] - metrics_2opt['total_distance']) / 
                        metrics_initial['total_distance'] * 100)
    report.append("2. AFTER 2-OPT OPTIMIZATION")
    report.append("-"*70)
    report.append(f"   Total Distance: {metrics_2opt['total_distance']:.2f}")
    report.append(f"   Improvement: {improvement_2opt:.2f}%")
    report.append("")
    
    # SA
    improvement_sa = ((metrics_initial['total_distance'] - metrics_sa['total_distance']) / 
                      metrics_initial['total_distance'] * 100)
    report.append("3. AFTER SIMULATED ANNEALING")
    report.append("-"*70)
    report.append(f"   Total Distance: {metrics_sa['total_distance']:.2f}")
    report.append(f"   Improvement: {improvement_sa:.2f}%")
    report.append("")
    
    # Best
    best_distance = min(metrics_initial['total_distance'], 
                       metrics_2opt['total_distance'], 
                       metrics_sa['total_distance'])
    if best_distance == metrics_sa['total_distance']:
        best_method = "Simulated Annealing"
    elif best_distance == metrics_2opt['total_distance']:
        best_method = "2-OPT"
    else:
        best_method = "Initial Greedy"
    
    report.append("4. SUMMARY")
    report.append("-"*70)
    report.append(f"   Best Method: {best_method}")
    report.append(f"   Best Total Distance: {best_distance:.2f}")
    overall_improvement = ((metrics_initial['total_distance'] - best_distance) / 
                          metrics_initial['total_distance'] * 100)
    report.append(f"   Overall Improvement: {overall_improvement:.2f}%")
    report.append("="*70)
    report.append("")
    
    report_text = "\n".join(report)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_text)
        print(f"Report saved to {output_file}")
    
    return report_text
