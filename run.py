#!/usr/bin/env python3
"""
Main Runner Script untuk Garbage Truck Route Planner
Mengeksekusi full pipeline: graph generation, initial solution, optimization, visualization
"""

import random
import os
from pathlib import Path

from src.graph import Graph
from src.greedy_init import greedy_initial_solution, TPS, Truck, format_routes_with_depot
from src.two_opt import optimize_routes_2opt, calculate_total_distance
from src.sa_optimizer import optimize_routes_sa
from src.vrp_solver import VRPSolver
from src.simulator import Simulator, visualize_comparison
from src.utils import (save_tps_to_csv, save_nodes_to_csv, save_routes_to_json,
                      print_routes, print_metrics, create_summary_report)


def main():
    """Main execution function"""
    print("="*70)
    print("GARBAGE TRUCK ROUTE PLANNER - OPTIMIZATION SYSTEM")
    print("="*70)
    print()
    
    # ========== STEP 1: CREATE GRAPH ==========
    print("STEP 1: Creating Graph Grid...")
    print("-"*70)
    
    graph = Graph()
    grid_width = 8
    grid_height = 6
    spacing = 1.0
    
    # Create obstacles
    obstacles = [(2, 3), (2, 4), (4, 1), (4, 2), (4, 3)]
    
    graph.load_from_grid(grid_width, grid_height, spacing, obstacles)
    print(f"✓ Graph created: {grid_width}x{grid_height} grid")
    print(f"  Total nodes: {len(graph.nodes)}")
    print(f"  Total edges: {len(graph.edges)}")
    print(f"  Obstacles: {len(obstacles)}")
    print()
    
    # ========== STEP 2: CREATE DEPOT & TPS ==========
    print("STEP 2: Setting up Depot and TPS...")
    print("-"*70)
    
    depot_id = "N3_0"  # Central depot
    print(f"✓ Depot set at {depot_id}")
    
    # Generate random TPS
    random.seed(42)  # For reproducibility
    num_tps = 12
    tps_list = []
    tps_ids_set = set()
    
    # Coordinates untuk TPS (avoid obstacles)
    available_nodes = list(graph.nodes.keys())
    selected_nodes = random.sample(available_nodes, min(num_tps, len(available_nodes)))
    
    for i, node_id in enumerate(selected_nodes):
        if node_id != depot_id:
            tps_id = f"TPS_{i+1}"
            demand = random.uniform(20, 50)
            tps = TPS(tps_id, node_id, demand)
            tps_list.append(tps)
            tps_ids_set.add(node_id)
            print(f"  TPS_{i+1} at {node_id}: demand={demand:.1f}")
    
    print(f"✓ Created {len(tps_list)} TPS locations")
    print()
    
    # ========== STEP 3: CREATE TRUCKS ==========
    print("STEP 3: Setting up Trucks...")
    print("-"*70)
    
    trucks = [
        Truck("T1", capacity=150.0),
        Truck("T2", capacity=120.0),
    ]
    
    for truck in trucks:
        print(f"✓ {truck.id}: capacity = {truck.capacity}")
    
    total_demand = sum(tps.demand for tps in tps_list)
    total_capacity = sum(truck.capacity for truck in trucks)
    print(f"\nTotal TPS demand: {total_demand:.1f}")
    print(f"Total truck capacity: {total_capacity:.1f}")
    print(f"Capacity utilization: {(total_demand/total_capacity)*100:.1f}%")
    print()
    
    # ========== STEP 4: GENERATE INITIAL SOLUTION ==========
    print("STEP 4: Generating Initial Greedy Solution...")
    print("-"*70)
    
    routes_initial = greedy_initial_solution(graph, tps_list, depot_id, trucks)
    routes_initial_with_depot = format_routes_with_depot(routes_initial, depot_id)
    
    metrics_initial = {
        'total_distance': calculate_total_distance(graph, routes_initial_with_depot),
        'num_trucks': len(trucks),
        'num_stops': sum(len([n for n in route if n != depot_id]) 
                        for route in routes_initial_with_depot.values()),
        'distances_per_truck': {}
    }
    
    for truck_id, route in routes_initial_with_depot.items():
        distance = 0.0
        for i in range(len(route) - 1):
            distance += graph.euclidean(route[i], route[i+1])
        metrics_initial['distances_per_truck'][truck_id] = distance
    
    print("✓ Initial solution generated")
    print_routes(routes_initial_with_depot, "INITIAL GREEDY ROUTES")
    print_metrics(metrics_initial, "INITIAL SOLUTION METRICS")
    
    # ========== STEP 5: OPTIMIZE WITH 2-OPT ==========
    print("STEP 5: Optimizing with 2-OPT...")
    print("-"*70)
    
    routes_2opt = optimize_routes_2opt(graph, routes_initial_with_depot,
                                       improvement_threshold=0.001,
                                       max_iterations=1000)
    
    metrics_2opt = {
        'total_distance': calculate_total_distance(graph, routes_2opt),
        'num_trucks': len(trucks),
        'num_stops': sum(len([n for n in route if n != depot_id]) 
                        for route in routes_2opt.values()),
        'distances_per_truck': {}
    }
    
    for truck_id, route in routes_2opt.items():
        distance = 0.0
        for i in range(len(route) - 1):
            distance += graph.euclidean(route[i], route[i+1])
        metrics_2opt['distances_per_truck'][truck_id] = distance
    
    improvement_2opt = ((metrics_initial['total_distance'] - metrics_2opt['total_distance']) /
                       metrics_initial['total_distance'] * 100)
    
    print(f"✓ 2-OPT optimization completed")
    print(f"  Improvement: {improvement_2opt:.2f}%")
    print_routes(routes_2opt, "2-OPT OPTIMIZED ROUTES")
    print_metrics(metrics_2opt, "2-OPT SOLUTION METRICS")
    
    # ========== STEP 6: OPTIMIZE WITH SIMULATED ANNEALING ==========
    print("STEP 6: Optimizing with Simulated Annealing...")
    print("-"*70)
    
    routes_sa = optimize_routes_sa(graph, routes_initial_with_depot,
                                   depot_id,
                                   t0=100.0,
                                   cooling_rate=0.995,
                                   iter_per_temp=200,
                                   t_min=0.1)
    
    metrics_sa = {
        'total_distance': calculate_total_distance(graph, routes_sa),
        'num_trucks': len(trucks),
        'num_stops': sum(len([n for n in route if n != depot_id]) 
                        for route in routes_sa.values()),
        'distances_per_truck': {}
    }
    
    for truck_id, route in routes_sa.items():
        distance = 0.0
        for i in range(len(route) - 1):
            distance += graph.euclidean(route[i], route[i+1])
        metrics_sa['distances_per_truck'][truck_id] = distance
    
    improvement_sa = ((metrics_initial['total_distance'] - metrics_sa['total_distance']) /
                     metrics_initial['total_distance'] * 100)
    
    print(f"✓ Simulated Annealing optimization completed")
    print(f"  Improvement: {improvement_sa:.2f}%")
    print_routes(routes_sa, "SIMULATED ANNEALING OPTIMIZED ROUTES")
    print_metrics(metrics_sa, "SIMULATED ANNEALING METRICS")
    
    # ========== STEP 7: COMPUTE FULL PATHS WITH A* ==========
    print("STEP 7: Computing Full Paths with A*...")
    print("-"*70)
    
    solver = VRPSolver(graph, depot_id)
    
    full_paths_initial = solver.compute_full_paths_as_single_list(routes_initial_with_depot)
    full_paths_2opt = solver.compute_full_paths_as_single_list(routes_2opt)
    full_paths_sa = solver.compute_full_paths_as_single_list(routes_sa)
    
    print("✓ Full paths computed using A* algorithm")
    print()
    
    # ========== STEP 8: VISUALIZE RESULTS ==========
    print("STEP 8: Generating Visualizations...")
    print("-"*70)
    
    # Create output directory if not exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Visualize routes (TPS ordering)
    print("  Creating comparison visualization...")
    comparison_fig = visualize_comparison(
        graph, depot_id, tps_ids_set,
        routes_initial_with_depot,
        routes_2opt,
        routes_sa,
        output_file=str(output_dir / "routes_comparison.png"),
        figsize=(18, 6)
    )
    
    # Save individual visualizations
    simulator = Simulator(graph, depot_id)
    
    simulator.visualize_routes(
        routes_initial_with_depot, tps_ids_set,
        title="Initial Greedy Solution",
        output_file=str(output_dir / "routes_initial.png")
    )
    
    simulator.visualize_routes(
        routes_2opt, tps_ids_set,
        title="After 2-OPT Optimization",
        output_file=str(output_dir / "routes_2opt.png")
    )
    
    simulator.visualize_routes(
        routes_sa, tps_ids_set,
        title="After Simulated Annealing Optimization",
        output_file=str(output_dir / "routes_sa.png")
    )
    
    print("✓ Visualizations saved to output/ directory")
    print()
    
    # ========== STEP 9: GENERATE REPORT ==========
    print("STEP 9: Generating Report...")
    print("-"*70)
    
    report = create_summary_report(
        metrics_initial, metrics_2opt, metrics_sa,
        output_file=str(output_dir / "optimization_report.txt")
    )
    print(report)
    
    # Save data to CSV
    save_tps_to_csv(tps_list, str(output_dir / "tps_locations.csv"))
    save_nodes_to_csv(graph, str(output_dir / "graph_nodes.csv"))
    save_routes_to_json(routes_initial_with_depot, str(output_dir / "routes_initial.json"))
    save_routes_to_json(routes_2opt, str(output_dir / "routes_2opt.json"))
    save_routes_to_json(routes_sa, str(output_dir / "routes_sa.json"))
    
    print()
    print("="*70)
    print("✓ OPTIMIZATION COMPLETED SUCCESSFULLY")
    print("="*70)
    print(f"\nOutput files saved to: {output_dir.absolute()}")
    print("\nFiles generated:")
    print("  - routes_comparison.png (side-by-side comparison)")
    print("  - routes_initial.png")
    print("  - routes_2opt.png")
    print("  - routes_sa.png")
    print("  - optimization_report.txt")
    print("  - tps_locations.csv")
    print("  - graph_nodes.csv")
    print("  - routes_initial.json")
    print("  - routes_2opt.json")
    print("  - routes_sa.json")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
