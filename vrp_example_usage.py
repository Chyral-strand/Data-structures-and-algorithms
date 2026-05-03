"""
Example usage of the VRP Graph Generator
Demonstrates different configurations and visualizations
"""

from vrp_graph_generator import VRPGraphGenerator
import matplotlib.pyplot as plt


def example_1_basic_graph():
    """Example 1: Generate and visualize a basic VRP graph"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic VRP Graph (20 customers)")
    print("="*60)
    
    generator = VRPGraphGenerator(
        num_customers=20,
        grid_size=100,
        seed=42,
        max_demand=10
    )
    nodes, distance_matrix = generator.generate_graph()
    generator.print_graph_info()
    
    fig, ax = generator.visualize(figsize=(12, 10), show_edges=True, show_demands=True)
    plt.savefig('vrp_example_1_basic.png', dpi=150, bbox_inches='tight')
    print("Saved: vrp_example_1_basic.png\n")
    plt.close()


def example_2_large_scale():
    """Example 2: Large-scale problem with many customers"""
    print("="*60)
    print("EXAMPLE 2: Large-Scale VRP Graph (50 customers)")
    print("="*60)
    
    generator = VRPGraphGenerator(
        num_customers=50,
        grid_size=200,
        seed=99,
        max_demand=15
    )
    nodes, distance_matrix = generator.generate_graph()
    generator.print_graph_info()
    
    # Visualize without edges for clarity
    fig, ax = generator.visualize(figsize=(14, 12), show_edges=False, show_demands=True)
    plt.savefig('vrp_example_2_large.png', dpi=150, bbox_inches='tight')
    print("Saved: vrp_example_2_large.png\n")
    plt.close()


def example_3_custom_parameters():
    """Example 3: Custom parameters with high demand"""
    print("="*60)
    print("EXAMPLE 3: Custom Parameters (Variable Demands)")
    print("="*60)
    
    generator = VRPGraphGenerator(
        num_customers=25,
        grid_size=120,
        seed=55,
        max_demand=20  # Higher demand variability
    )
    nodes, distance_matrix = generator.generate_graph()
    generator.print_graph_info()
    
    fig, ax = generator.visualize(figsize=(13, 11), show_edges=True, show_demands=True)
    plt.savefig('vrp_example_3_custom.png', dpi=150, bbox_inches='tight')
    print("Saved: vrp_example_3_custom.png\n")
    plt.close()


def example_4_multiple_variants():
    """Example 4: Create multiple graphs side-by-side for comparison"""
    print("="*60)
    print("EXAMPLE 4: Multiple Graph Variants Comparison")
    print("="*60)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('VRP Graph Variants Comparison', fontsize=16, fontweight='bold')
    
    configs = [
        {"num_customers": 15, "grid_size": 100, "seed": 10, "title": "Small (15 customers)"},
        {"num_customers": 25, "grid_size": 120, "seed": 20, "title": "Medium (25 customers)"},
        {"num_customers": 35, "grid_size": 150, "seed": 30, "title": "Large (35 customers)"},
        {"num_customers": 40, "grid_size": 160, "seed": 40, "title": "XL (40 customers)"},
    ]
    
    for idx, (ax, config) in enumerate(zip(axes.flat, configs)):
        generator = VRPGraphGenerator(
            num_customers=config["num_customers"],
            grid_size=config["grid_size"],
            seed=config["seed"],
            max_demand=10
        )
        nodes, distance_matrix = generator.generate_graph()
        
        # Plot on provided axis
        depot_node = nodes[0]
        customer_nodes = nodes[1:]
        
        # Plot edges
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                node_i = nodes[i]
                node_j = nodes[j]
                ax.plot([node_i.x, node_j.x], [node_i.y, node_j.y], 
                       'gray', alpha=0.1, linewidth=0.5)
        
        # Plot depot
        ax.scatter(depot_node.x, depot_node.y, s=300, c='red', marker='s', 
                  edgecolors='darkred', linewidth=2, zorder=3)
        
        # Plot customers
        if customer_nodes:
            customer_x = [node.x for node in customer_nodes]
            customer_y = [node.y for node in customer_nodes]
            demands = [node.demand for node in customer_nodes]
            
            scatter = ax.scatter(customer_x, customer_y, s=150, c=demands, 
                               cmap='viridis', edgecolors='black', linewidth=0.5, alpha=0.7)
        
        ax.set_title(config["title"], fontsize=12, fontweight='bold')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('vrp_example_4_comparison.png', dpi=150, bbox_inches='tight')
    print("Saved: vrp_example_4_comparison.png\n")
    plt.close()


def example_5_distance_analysis():
    """Example 5: Analyze distance matrix statistics"""
    print("="*60)
    print("EXAMPLE 5: Distance Matrix Analysis")
    print("="*60)
    
    generator = VRPGraphGenerator(
        num_customers=20,
        grid_size=100,
        seed=77,
        max_demand=10
    )
    nodes, distance_matrix = generator.generate_graph()
    
    # Filter out zero distances (diagonal)
    import numpy as np
    distances = distance_matrix[distance_matrix > 0]
    
    print(f"Number of nodes: {len(nodes)}")
    print(f"Distance matrix shape: {distance_matrix.shape}")
    print(f"\nDistance Statistics (non-zero):")
    print(f"  Minimum distance: {distances.min():.2f}")
    print(f"  Maximum distance: {distances.max():.2f}")
    print(f"  Mean distance:    {distances.mean():.2f}")
    print(f"  Median distance:  {np.median(distances):.2f}")
    print(f"  Std deviation:    {distances.std():.2f}")
    
    # Visualize with distance heatmap
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left plot: Graph visualization
    depot_node = nodes[0]
    customer_nodes = nodes[1:]
    
    ax1.scatter(depot_node.x, depot_node.y, s=400, c='red', marker='s', 
               label='Depot', zorder=3, edgecolors='darkred', linewidth=2)
    
    if customer_nodes:
        customer_x = [node.x for node in customer_nodes]
        customer_y = [node.y for node in customer_nodes]
        ax1.scatter(customer_x, customer_y, s=200, c='blue', alpha=0.6, 
                   label='Customers', zorder=2, edgecolors='black')
    
    ax1.set_title('VRP Graph Layout', fontsize=12, fontweight='bold')
    ax1.set_xlabel('X Coordinate')
    ax1.set_ylabel('Y Coordinate')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    
    # Right plot: Distance heatmap
    im = ax2.imshow(distance_matrix, cmap='hot', aspect='auto')
    ax2.set_title('Distance Matrix Heatmap', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Node ID')
    ax2.set_ylabel('Node ID')
    plt.colorbar(im, ax=ax2, label='Distance')
    
    plt.tight_layout()
    plt.savefig('vrp_example_5_analysis.png', dpi=150, bbox_inches='tight')
    print("Saved: vrp_example_5_analysis.png\n")
    plt.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("VRP GRAPH GENERATOR - USAGE EXAMPLES")
    print("="*60)
    
    # Run all examples
    example_1_basic_graph()
    example_2_large_scale()
    example_3_custom_parameters()
    example_4_multiple_variants()
    example_5_distance_analysis()
    
    print("="*60)
    print("All examples completed successfully!")
    print("Generated images:")
    print("  - vrp_example_1_basic.png")
    print("  - vrp_example_2_large.png")
    print("  - vrp_example_3_custom.png")
    print("  - vrp_example_4_comparison.png")
    print("  - vrp_example_5_analysis.png")
    print("="*60 + "\n")
