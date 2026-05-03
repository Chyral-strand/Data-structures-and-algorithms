"""
Interactive VRP Solver with GUI
Allows users to generate random VRP graphs and run different routing algorithms
with step-by-step visualization and explanations.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from vrp_graph_generator import VRPGraphGenerator
import time


class VRPInteractiveSolver:
    """Interactive VRP solver with GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("VRP Interactive Solver")
        self.root.geometry("1600x900")
        
        self.generator = None
        self.nodes = None
        self.distance_matrix = None
        self.current_route = None
        self.total_distance = 0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Graph visualization
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Canvas for matplotlib
        self.fig = Figure(figsize=(8, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=left_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Controls and info
        right_frame = ttk.Frame(main_frame, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        right_frame.pack_propagate(False)
        
        # Title
        title_label = ttk.Label(right_frame, text="VRP Interactive Solver", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Graph generation section
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        gen_label = ttk.Label(right_frame, text="Graph Generation", 
                             font=("Arial", 11, "bold"))
        gen_label.pack(pady=5)
        
        ttk.Button(right_frame, text="Generate Small Graph (10 nodes)", 
                  command=lambda: self._generate_graph("small")).pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(right_frame, text="Generate Large Graph (50 nodes)", 
                  command=lambda: self._generate_graph("large")).pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(right_frame, text="Generate Extra Large Graph (300 nodes)", 
                  command=lambda: self._generate_graph("xlarge")).pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(right_frame, text="Save Current Graph to JSON", 
                  command=self._save_to_json).pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(right_frame, text="Load Graph from JSON", 
                  command=self._load_from_json).pack(fill=tk.X, padx=10, pady=5)
        
        # Algorithm selection section
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        algo_label = ttk.Label(right_frame, text="Select Algorithm", 
                              font=("Arial", 11, "bold"))
        algo_label.pack(pady=5)
        
        ttk.Button(right_frame, text="1. Nearest Neighbor", 
                  command=lambda: self._run_algorithm("nearest_neighbor")).pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(right_frame, text="2. Savings Algorithm", 
                  command=lambda: self._run_algorithm("savings")).pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(right_frame, text="3. Two-Opt Improvement", 
                  command=lambda: self._run_algorithm("two_opt")).pack(fill=tk.X, padx=10, pady=5)
        
        # Info section
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        info_label = ttk.Label(right_frame, text="Graph Info", 
                              font=("Arial", 11, "bold"))
        info_label.pack(pady=5)
        
        self.info_text = tk.Text(right_frame, height=8, width=45, 
                                state=tk.DISABLED, font=("Courier", 9))
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Execution log section
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        log_label = ttk.Label(right_frame, text="Execution Log", 
                             font=("Arial", 11, "bold"))
        log_label.pack(pady=5)
        
        self.log_text = tk.Text(right_frame, height=8, width=45, 
                               state=tk.DISABLED, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.config(yscroll=scrollbar.set)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5, side=tk.LEFT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize with a small graph
        self._generate_graph("small")
    
    def _generate_graph(self, size="small"):
        """Generate a new random VRP graph"""
        try:
            # Predefined configurations for small, large, and extra large graphs
            if size == "small":
                num_customers = 10
                grid_size = 100
                max_demand = 10
                min_distance = 10.0
                self._add_log("Generating small graph (10 nodes)...")
            elif size == "large":
                num_customers = 50
                grid_size = 150
                max_demand = 10
                min_distance = 10.0
                self._add_log("Generating large graph (50 nodes)...")
            else:  # xlarge
                num_customers = 300
                grid_size = 300
                max_demand = 10
                min_distance = 3.0
                self._add_log("Generating extra large graph (300 nodes)...")
                self._add_log("This may take a moment...")
            
            self.generator = VRPGraphGenerator(
                num_customers=num_customers,
                grid_size=grid_size,
                max_demand=max_demand,
                min_node_distance=min_distance,
                seed=None  # Random seed each time
            )
            
            self.nodes, self.distance_matrix = self.generator.generate_graph()
            self.current_route = None
            self.total_distance = 0
            
            self._update_graph_visualization()
            self._update_info()
            self._add_log("Graph generated successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def _save_to_json(self):
        """Save the current graph to a JSON file"""
        if self.nodes is None:
            messagebox.showwarning("Warning", "Please generate a graph first!")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save VRP Graph as JSON"
            )
            
            if not file_path:
                return  # User cancelled
            
            self.generator.save_to_json(file_path)
            self._add_log(f"Graph saved to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON file: {e}")
    
    def _load_from_json(self):
        """Load VRP graph from a JSON file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select JSON file",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not file_path:
                return  # User cancelled
            
            self._add_log(f"Loading graph from {file_path}...")
            
            # Create generator and load from JSON
            self.generator = VRPGraphGenerator()  # Default parameters, not used for loading
            self.nodes, self.distance_matrix = self.generator.load_from_json(file_path)
            
            self.current_route = None
            self.total_distance = 0
            
            self._update_graph_visualization()
            self._update_info()
            self._add_log("Graph loaded successfully from JSON!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {e}")
            self._add_log(f"Error loading JSON: {e}")
    
    def _update_graph_visualization(self):
        """Update the graph visualization"""
        self.ax.clear()
        
        depot_node = self.nodes[0]
        customer_nodes = self.nodes[1:]
        
        # Plot edges (k-nearest neighbors)
        k_neighbors = 5
        edges_drawn = set()
        
        for i in range(len(self.nodes)):
            distances_from_i = self.distance_matrix[i].copy()
            distances_from_i[i] = np.inf
            nearest_indices = np.argsort(distances_from_i)[:k_neighbors]
            
            for j in nearest_indices:
                if i < j:
                    edge_key = (i, j)
                    if edge_key not in edges_drawn:
                        node_i = self.nodes[i]
                        node_j = self.nodes[j]
                        distance = self.distance_matrix[i][j]
                        
                        alpha = 0.3
                        self.ax.plot([node_i.x, node_j.x], [node_i.y, node_j.y], 
                                   'gray', alpha=alpha, linewidth=1, zorder=1)
                        
                        mid_x = (node_i.x + node_j.x) / 2
                        mid_y = (node_i.y + node_j.y) / 2
                        self.ax.text(mid_x, mid_y, f'{distance:.0f}', 
                                   fontsize=6, ha='center', va='center',
                                   bbox=dict(boxstyle='round,pad=0.2', 
                                            facecolor='white', alpha=0.7, edgecolor='none'),
                                   zorder=2)
                        edges_drawn.add(edge_key)
        
        # Plot depot
        self.ax.scatter(depot_node.x, depot_node.y, s=400, c='red', marker='s', 
                       label='Depot', zorder=3, edgecolors='darkred', linewidth=2)
        
        # Plot customers
        if customer_nodes:
            customer_x = [node.x for node in customer_nodes]
            customer_y = [node.y for node in customer_nodes]
            demands = [node.demand for node in customer_nodes]
            
            self.ax.scatter(customer_x, customer_y, s=200, c=demands, 
                           cmap='viridis', label='Customers', zorder=2,
                           edgecolors='black', linewidth=1, alpha=0.8)
            
            for node in customer_nodes:
                self.ax.text(node.x, node.y - 2.5, f'C{node.id}', 
                           ha='center', fontsize=7, fontweight='bold')
        
        # Draw current route if exists
        if self.current_route:
            for idx in range(len(self.current_route) - 1):
                node_from = self.nodes[self.current_route[idx]]
                node_to = self.nodes[self.current_route[idx + 1]]
                self.ax.plot([node_from.x, node_to.x], [node_from.y, node_to.y], 
                           'b-', linewidth=2, alpha=0.6, zorder=4)
        
        self.ax.set_xlabel('X Coordinate', fontsize=10)
        self.ax.set_ylabel('Y Coordinate', fontsize=10)
        self.ax.set_title(f'VRP Graph ({len(self.nodes)-1} customers + 1 depot)', 
                         fontsize=11, fontweight='bold')
        self.ax.legend(loc='upper right', fontsize=9)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _update_info(self):
        """Update the info text box"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info = "GRAPH INFORMATION\n"
        info += "=" * 40 + "\n"
        info += f"Total Nodes: {len(self.nodes)}\n"
        info += f"  - Depot: 1\n"
        info += f"  - Customers: {len(self.nodes) - 1}\n"
        info += f"\nGrid Size: {self.generator.grid_size}x{self.generator.grid_size}\n"
        
        total_demand = sum(node.demand for node in self.nodes[1:])
        info += f"Total Demand: {total_demand}\n"
        
        if self.current_route:
            info += f"\nCURRENT ROUTE\n"
            info += "=" * 40 + "\n"
            route_str = " -> ".join(str(node_id) for node_id in self.current_route)
            info += f"{route_str}\n"
            info += f"Total Distance: {self.total_distance:.1f}\n"
        
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)
    
    def _add_log(self, message):
        """Add a message to the execution log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def _run_algorithm(self, algorithm_name):
        """Run the selected algorithm"""
        if self.nodes is None:
            messagebox.showwarning("Warning", "Please generate a graph first!")
            return
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        if algorithm_name == "nearest_neighbor":
            self._nearest_neighbor()
        elif algorithm_name == "savings":
            self._savings_algorithm()
        elif algorithm_name == "two_opt":
            self._two_opt_algorithm()
    
    def _nearest_neighbor(self):
        """Nearest Neighbor algorithm - greedy approach"""
        self._add_log("NEAREST NEIGHBOR ALGORITHM")
        self._add_log("=" * 40)
        self._add_log("Description: Start at depot, always move to")
        self._add_log("closest unvisited customer, return to depot.")
        self._add_log("\n--- Execution ---\n")
        
        self.current_route = [0]  # Start at depot
        unvisited = set(range(1, len(self.nodes)))
        current_node = 0
        total_distance = 0
        
        self._add_log(f"Step 1: Start at Depot (Node 0)")
        time.sleep(0.5)
        
        step = 2
        while unvisited:
            # Find nearest unvisited customer
            nearest_distance = float('inf')
            nearest_node = None
            
            for node_id in unvisited:
                dist = self.distance_matrix[current_node][node_id]
                if dist < nearest_distance:
                    nearest_distance = dist
                    nearest_node = node_id
            
            # Move to nearest node
            self.current_route.append(nearest_node)
            total_distance += nearest_distance
            unvisited.remove(nearest_node)
            
            self._add_log(f"Step {step}: Move to Node {nearest_node} (dist: {nearest_distance:.1f})")
            self._add_log(f"   Unvisited: {sorted(unvisited) if unvisited else 'None'}")
            
            current_node = nearest_node
            step += 1
            
            self._update_graph_visualization()
            time.sleep(0.3)
        
        # Return to depot
        return_distance = self.distance_matrix[current_node][0]
        self.current_route.append(0)
        total_distance += return_distance
        
        self._add_log(f"Step {step}: Return to Depot (dist: {return_distance:.1f})")
        
        self.total_distance = total_distance
        
        self._add_log(f"\n--- Result ---")
        self._add_log(f"Route: {' -> '.join(map(str, self.current_route))}")
        self._add_log(f"Total Distance: {self.total_distance:.1f}")
        
        self._update_graph_visualization()
        self._update_info()
    
    def _savings_algorithm(self):
        """Savings Algorithm (Clarke-Wright)"""
        self._add_log("SAVINGS ALGORITHM (Clarke-Wright)")
        self._add_log("=" * 40)
        self._add_log("Description: Calculate savings for combining")
        self._add_log("routes, merge most beneficial pairs first.")
        self._add_log("\n--- Execution ---\n")
        
        # Calculate savings
        self._add_log("Step 1: Calculate savings for all pairs:")
        savings_list = []
        
        for i in range(1, len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                # Savings = distance from depot to i + distance from depot to j
                #           - distance from i to j
                saving = (self.distance_matrix[0][i] + 
                         self.distance_matrix[0][j] - 
                         self.distance_matrix[i][j])
                savings_list.append((saving, i, j))
        
        savings_list.sort(reverse=True)
        
        self._add_log(f"   Found {len(savings_list)} possible pairs")
        self._add_log(f"   Top 5 savings:")
        for idx, (saving, i, j) in enumerate(savings_list[:5]):
            self._add_log(f"     {idx+1}. Nodes {i}-{j}: {saving:.1f}")
        
        time.sleep(0.5)
        
        # Build routes using best savings
        routes = [[i] for i in range(1, len(self.nodes))]
        
        self._add_log(f"\nStep 2: Merge routes based on savings:")
        
        pairs_merged = 0
        for saving, i, j in savings_list:
            # Find routes containing i and j
            route_i = None
            route_j = None
            
            for route in routes:
                if i in route:
                    route_i = route
                if j in route:
                    route_j = route
            
            # Merge if in different routes and touching ends
            if route_i and route_j and route_i != route_j:
                if route_i[-1] == i and route_j[0] == j:
                    routes.remove(route_i)
                    routes.remove(route_j)
                    routes.append(route_i + route_j)
                    pairs_merged += 1
                    self._add_log(f"   Merged: {route_i} + {route_j}")
                    time.sleep(0.2)
        
        # Convert routes to single route for visualization
        self.current_route = [0]
        total_distance = 0
        
        for route in routes:
            for node in route:
                self.current_route.append(node)
                if len(self.current_route) > 1:
                    total_distance += self.distance_matrix[self.current_route[-2]][node]
        
        self.current_route.append(0)
        total_distance += self.distance_matrix[self.current_route[-2]][0]
        self.total_distance = total_distance
        
        self._add_log(f"\n--- Result ---")
        self._add_log(f"Routes merged: {pairs_merged}")
        self._add_log(f"Route: {' -> '.join(map(str, self.current_route))}")
        self._add_log(f"Total Distance: {self.total_distance:.1f}")
        
        self._update_graph_visualization()
        self._update_info()
    
    def _two_opt_algorithm(self):
        """Two-Opt local search improvement"""
        self._add_log("TWO-OPT IMPROVEMENT ALGORITHM")
        self._add_log("=" * 40)
        self._add_log("Description: Start with nearest neighbor,")
        self._add_log("improve by reversing route segments.")
        self._add_log("\n--- Execution ---\n")
        
        # First, get initial route using nearest neighbor
        self._add_log("Step 1: Generate initial route (Nearest Neighbor)")
        
        self.current_route = [0]
        unvisited = set(range(1, len(self.nodes)))
        current_node = 0
        total_distance = 0
        
        while unvisited:
            nearest_distance = float('inf')
            nearest_node = None
            
            for node_id in unvisited:
                dist = self.distance_matrix[current_node][node_id]
                if dist < nearest_distance:
                    nearest_distance = dist
                    nearest_node = node_id
            
            self.current_route.append(nearest_node)
            total_distance += nearest_distance
            unvisited.remove(nearest_node)
            current_node = nearest_node
        
        return_distance = self.distance_matrix[current_node][0]
        self.current_route.append(0)
        total_distance += return_distance
        
        self._add_log(f"   Initial route distance: {total_distance:.1f}")
        
        self._update_graph_visualization()
        time.sleep(0.5)
        
        # Two-Opt improvements
        self._add_log(f"\nStep 2: Apply 2-Opt improvements...")
        
        improved = True
        iteration = 0
        best_distance = total_distance
        
        while improved and iteration < 20:
            improved = False
            iteration += 1
            
            for i in range(1, len(self.current_route) - 2):
                for j in range(i + 2, len(self.current_route)):
                    # Calculate distance change
                    a, b = self.current_route[i-1], self.current_route[i]
                    c, d = self.current_route[j-1], self.current_route[j]
                    
                    old_dist = self.distance_matrix[a][b] + self.distance_matrix[c][d]
                    new_dist = self.distance_matrix[a][c] + self.distance_matrix[b][d]
                    
                    if new_dist < old_dist:
                        # Reverse the segment
                        self.current_route[i:j] = self.current_route[i:j][::-1]
                        best_distance -= (old_dist - new_dist)
                        improved = True
                        
                        self._add_log(f"   Iteration {iteration}: Improved! New distance: {best_distance:.1f}")
                        self._update_graph_visualization()
                        time.sleep(0.3)
                        break
                
                if improved:
                    break
        
        self.total_distance = best_distance
        
        self._add_log(f"\n--- Result ---")
        self._add_log(f"Iterations completed: {iteration}")
        self._add_log(f"Route: {' -> '.join(map(str, self.current_route))}")
        self._add_log(f"Final Distance: {self.total_distance:.1f}")
        
        self._update_graph_visualization()
        self._update_info()


def main():
    root = tk.Tk()
    app = VRPInteractiveSolver(root)
    root.mainloop()


if __name__ == "__main__":
    main()
