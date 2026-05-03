import random
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import json


@dataclass
class Node:
    """Represents a node (depot or customer) in the VRP graph"""
    id: int
    x: float
    y: float
    demand: int = 0  # 0 for depot, > 0 for customers
    is_depot: bool = False


class VRPGraphGenerator:
    """Generates randomized VRP graphs with visualization"""
    
    def __init__(self, num_customers: int = 20, grid_size: int = 100, 
                 seed: int = 1, max_demand: int = 10, min_node_distance: float = 10.0):
        """
        Initialize the VRP graph generator
        
        Args:
            num_customers: Number of customer nodes to generate
            grid_size: Size of the grid for node placement (0 to grid_size)
            seed: Random seed for reproducibility
            max_demand: Maximum demand for each customer
            min_node_distance: Minimum allowed distance between any two nodes
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        self.num_customers = num_customers
        self.grid_size = grid_size
        self.max_demand = max_demand
        self.min_node_distance = min_node_distance
        self.nodes: List[Node] = []
        self.distance_matrix = None
    
    def generate_graph(self) -> Tuple[List[Node], np.ndarray]:
        """
        Generate a random VRP graph with minimum distance constraint
        
        Returns:
            Tuple of (nodes list, distance matrix)
        """
        self.nodes = []
        
        # Create depot (always at center)
        depot = Node(
            id=0,
            x=self.grid_size / 2,
            y=self.grid_size / 2,
            demand=0,
            is_depot=True
        )
        self.nodes.append(depot)
        
        # Create customer nodes with minimum distance constraint
        customers_created = 0
        max_attempts = 1000  # Prevent infinite loop
        attempts = 0
        
        while customers_created < self.num_customers and attempts < max_attempts:
            attempts += 1
            
            # Generate random position
            x = random.uniform(0, self.grid_size)
            y = random.uniform(0, self.grid_size)
            
            # Check minimum distance constraint with all existing nodes
            too_close = False
            for existing_node in self.nodes:
                distance = np.sqrt((x - existing_node.x)**2 + (y - existing_node.y)**2)
                if distance < self.min_node_distance:
                    too_close = True
                    break
            
            # If far enough from all nodes, add the customer
            if not too_close:
                customer = Node(
                    id=customers_created + 1,
                    x=x,
                    y=y,
                    demand=random.randint(1, self.max_demand),
                    is_depot=False
                )
                self.nodes.append(customer)
                customers_created += 1
        
        if customers_created < self.num_customers:
            print(f"Warning: Could only place {customers_created} out of {self.num_customers} customers.")
            print(f"Try reducing min_node_distance, increasing grid_size, or decreasing num_customers.")
        
        # Calculate distance matrix
        self._calculate_distances()
        
        return self.nodes, self.distance_matrix
    
    def _calculate_distances(self):
        """Calculate Euclidean distances between all nodes"""
        n = len(self.nodes)
        self.distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    node_i = self.nodes[i]
                    node_j = self.nodes[j]
                    distance = np.sqrt((node_i.x - node_j.x)**2 + 
                                      (node_i.y - node_j.y)**2)
                    self.distance_matrix[i][j] = distance
    
    def save_to_json(self, json_file_path: str):
        """
        Save the current VRP graph to a JSON file
        
        Args:
            json_file_path: Path where to save the JSON file
        """
        if not self.nodes:
            raise ValueError("No graph generated. Call generate_graph() first.")
        
        # Find depot and customers
        depot = None
        customers = []
        
        for node in self.nodes:
            if node.is_depot:
                depot = {"x": node.x, "y": node.y}
            else:
                customers.append({
                    "id": node.id,
                    "x": node.x,
                    "y": node.y,
                    "demand": node.demand
                })
        
        # Create JSON structure
        data = {
            "depot": depot,
            "customers": customers
        }
        
        # Save to file
        with open(json_file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_json(self, json_file_path: str) -> Tuple[List[Node], np.ndarray]:
        """
        Load VRP graph from a JSON file
        
        Expected JSON format:
        {
            "depot": {"x": float, "y": float},
            "customers": [
                {"id": int, "x": float, "y": float, "demand": int},
                ...
            ]
        }
        
        Args:
            json_file_path: Path to the JSON file
            
        Returns:
            Tuple of (nodes list, distance matrix)
        """
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        self.nodes = []
        
        # Load depot
        depot_data = data['depot']
        depot = Node(
            id=0,
            x=depot_data['x'],
            y=depot_data['y'],
            demand=0,
            is_depot=True
        )
        self.nodes.append(depot)
        
        # Load customers
        for customer_data in data['customers']:
            customer = Node(
                id=customer_data['id'],
                x=customer_data['x'],
                y=customer_data['y'],
                demand=customer_data['demand'],
                is_depot=False
            )
            self.nodes.append(customer)
        
        # Calculate distance matrix
        self._calculate_distances()
        
        return self.nodes, self.distance_matrix
    
    def visualize(self, figsize: Tuple[int, int] = (12, 10), 
                  show_edges: bool = True, show_demands: bool = True,
                  k_neighbors: int = 5):
        """
        Visualize the VRP graph using matplotlib
        
        Args:
            figsize: Figure size (width, height)
            show_edges: Whether to draw edges between nodes
            show_demands: Whether to display demand values
            k_neighbors: Number of nearest neighbors to connect each node to
        """
        if not self.nodes:
            raise ValueError("No graph generated. Call generate_graph() first.")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Extract coordinates
        depot_node = self.nodes[0]
        customer_nodes = self.nodes[1:]
        
        # Plot edges to k-nearest neighbors (optional)
        if show_edges and len(self.nodes) > 1:
            edges_drawn = set()  # Track edges to avoid duplicates
            
            for i in range(len(self.nodes)):
                # Get distances from node i to all other nodes
                distances_from_i = self.distance_matrix[i].copy()
                distances_from_i[i] = np.inf  # Exclude self
                
                # Find indices of k nearest neighbors
                nearest_indices = np.argsort(distances_from_i)[:k_neighbors]
                
                # Draw edges to nearest neighbors
                for j in nearest_indices:
                    if i < j:  # Only draw once per edge
                        edge_key = (i, j)
                        if edge_key not in edges_drawn:
                            node_i = self.nodes[i]
                            node_j = self.nodes[j]
                            distance = self.distance_matrix[i][j]
                            
                            # Color edge based on distance (shorter = darker)
                            alpha = 0.35 + (1 - distance / distances_from_i[nearest_indices].max()) * 0.4
                            ax.plot([node_i.x, node_j.x], [node_i.y, node_j.y], 
                                   'gray', alpha=alpha, linewidth=1, zorder=1)
                            
                            # Add distance label at midpoint
                            mid_x = (node_i.x + node_j.x) / 2
                            mid_y = (node_i.y + node_j.y) / 2
                            ax.text(mid_x, mid_y, f'{distance:.0f}', 
                                   fontsize=7, ha='center', va='center',
                                   bbox=dict(boxstyle='round,pad=0.3', 
                                            facecolor='white', alpha=0.8, edgecolor='none'),
                                   zorder=2)
                            edges_drawn.add(edge_key)
        
        # Plot depot
        ax.scatter(depot_node.x, depot_node.y, s=400, c='red', marker='s', 
                  label='Depot', zorder=3, edgecolors='darkred', linewidth=2)
        ax.text(depot_node.x, depot_node.y - 3, 'Depot', 
               ha='center', fontsize=10, fontweight='bold')
        
        # Plot customer nodes
        if customer_nodes:
            customer_x = [node.x for node in customer_nodes]
            customer_y = [node.y for node in customer_nodes]
            demands = [node.demand for node in customer_nodes]
            
            scatter = ax.scatter(customer_x, customer_y, s=200, c=demands, 
                               cmap='viridis', label='Customers', zorder=2,
                               edgecolors='black', linewidth=1, alpha=0.8)
            
            # Add node labels and demands
            for node in customer_nodes:
                ax.text(node.x, node.y - 2.5, f'C{node.id}', 
                       ha='center', fontsize=8, fontweight='bold')
                if show_demands:
                    ax.text(node.x, node.y + 2, f'd={node.demand}', 
                           ha='center', fontsize=7, style='italic', color='gray')
        
        # Set labels and title
        ax.set_xlabel('X Coordinate', fontsize=12)
        ax.set_ylabel('Y Coordinate', fontsize=12)
        ax.set_title(f'Vehicle Routing Problem Graph\n({self.num_customers} customers + 1 depot)', 
                    fontsize=14, fontweight='bold')
        
        # Set axis limits with padding
        padding = 5
        ax.set_xlim(-padding, self.grid_size + padding)
        ax.set_ylim(-padding, self.grid_size + padding)
        
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_aspect('equal')
        
        plt.tight_layout()
        
        return fig, ax
    
    def print_graph_info(self):
        """Print information about the generated graph"""
        if not self.nodes:
            print("No graph generated yet.")
            return
        
        print("=" * 50)
        print("VRP Graph Information")
        print("=" * 50)
        print(f"Number of nodes: {len(self.nodes)}")
        print(f"  - Depot: 1")
        print(f"  - Customers: {len(self.nodes) - 1}")
        print(f"\nGrid size: {self.grid_size} x {self.grid_size}")
        print(f"\nNode Details:")
        print(f"{'ID':<5} {'Type':<10} {'X':<8} {'Y':<8} {'Demand':<8}")
        print("-" * 40)
        
        for node in self.nodes:
            node_type = "Depot" if node.is_depot else "Customer"
            print(f"{node.id:<5} {node_type:<10} {node.x:<8.2f} {node.y:<8.2f} {node.demand:<8}")
        
        print(f"\nTotal demand: {sum(node.demand for node in self.nodes[1:])}")
        print("=" * 50)
        print()


def main():
    """Main function to demonstrate the VRP graph generator"""
    
    # Create generator and generate graph
    print("Generating randomized VRP graph...")
    generator = VRPGraphGenerator(
        num_customers=25,
        grid_size=100,
        seed=42,  # For reproducibility
        max_demand=10
    )
    
    nodes, distance_matrix = generator.generate_graph()
    
    # Print graph information
    generator.print_graph_info()
    
    # Visualize the graph
    print("\nGenerating visualization...")
    fig, ax = generator.visualize(figsize=(14, 10), show_edges=True, show_demands=True)
    
    plt.show()


if __name__ == "__main__":
    main()
