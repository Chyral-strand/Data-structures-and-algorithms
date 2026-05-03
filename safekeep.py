import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from graphgenerator import GraphGenerator
import time

class VRPSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("VRP Solver")
        self.root.geometry("1600x900")

        self.generator = None
        self.nodes = None
        self.distancematrix = None
        self.current_route = None
        self.total_distance = 0
        self._setup()

    def _setup(self):
        main_frame = ttk.Frame(self.root) ## Background
        main_frame.pack(fill = tk.BOTH, expand = True, padx = 5, pady = 5)

        left_frame = ttk.Frame(main_frame) ## Left-hand graph display
        left_frame.pack(side = tk.LEFT, fill = tk.BOTH, expand = True, padx = 5)
        self.fig = Figure(figsize = (8,8), dpi = 100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master = left_frame)
        self.canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)

        right_frame = ttk.Frame(main_frame, width = 400) ## Right-hand UI panel
        right_frame.pack(side = tk.RIGHT, fill = tk.BOTH, padx = 5)
        right_frame.pack_propagate(False)
        title_label = ttk.Label(right_frame, text = "VRP Solver")
        title_label.pack(pady = 10)
            
        gen_label = ttk.Label(right_frame, text = "Graph generation")
        gen_label.pack(pady = 5)
        ttk.Button(right_frame, text = "Select Graph JSON File", command = self._load_from_json).pack(fill = tk.X, padx = 10, pady = 5)
        ttk.Button(right_frame, text = "Clear graph", command = self._clear_graph).pack(fill = tk.X, padx = 10, pady = 5)

        algorithm_label = ttk.Label(right_frame, text = "Algorithms")
        algorithm_label.pack(pady = 5)
        ttk.Button(right_frame, text = "Algorithm 1: Brute-force", command = lambda: self._run_algorithm("simple")).pack(fill = tk.X, padx = 10, pady = 5)
        ttk.Button(right_frame, text = "Algorithm 2: ", command = lambda: self._run_algorithm("complex")).pack(fill = tk.X, padx = 10, pady = 5)
        ttk.Button(right_frame, text = "Algorithm 3: ", command = lambda: self._run_algorithm("ai")).pack(fill = tk.X, padx = 10, pady = 5)

        info_label = ttk.Label(right_frame, text = "Graph Info")
        info_label.pack(pady = 5)
        self.info_text = tk.Text(right_frame, height = 4, width = 20, state = tk.DISABLED)
        self.info_text.pack(fill = tk.BOTH, expand = True, padx = 10, pady = 5)

        log_label = ttk.Label(right_frame, text = "Execution Log")
        log_label.pack(pady = 5)
        self.log_text = tk.Text(right_frame, height = 6, width = 40, state = tk.DISABLED)
        logscrollbar = ttk.Scrollbar(right_frame, orient = tk.VERTICAL, command = self.log_text.yview)
        self.log_text.config(yscroll = logscrollbar.set)
        self.log_text.pack(fill = tk.BOTH, expand = True, padx = 10, pady = 5, side = tk.LEFT)
        logscrollbar.pack(fill = tk.Y, side = tk.RIGHT)

        self.generate_graph("base")

    def generate_graph (self, graphname = "base"):
        try:
            if graphname == "base":
                num_customers = 10
                grid_size = 100
                self._add_log("Generating base graph (10 nodes)")
            self.generator = GraphGenerator(num_customers = num_customers, grid_size = grid_size, graph_id = None) ## Produces a random graph with 10 customers
            self.customers, self.distance_matrix = self.generator.generate_graph()
            self.current_route = None
            self.total_distance = 0

            self._update_graph_vis()
            self._update_info()
            self._add_log("Graph generated successfully!")
            
        except ValueError as e: messagebox.showerror("Error", f"Invalid input: {e}")

    def _clear_graph(self): ## Empties plot, redraws nodes and edges then updates display
        self.ax.clear()
        if self.customers:
            self._update_graph_vis()
        else:
            self._add_log("No graph data to clear")
        self.canvas.draw()

    def _load_from_json(self):
        try:
            file_path = filedialog.askopenfilename(title = "Select test case file", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if not file_path:
                return
            self._add_log(f"Loading graph from {file_path}")

            self.generator = GraphGenerator()
            self.customers, self.distance_matrix = self.generator.load_from_json(file_path)
            self._update_graph_vis()
            self._update_info()
            self._add_log("Graph loaded successfully from JSON")
        except Exception as e:
            messagebox.showerror("Error", f"failed to load JSON file: {e}")
            self._add_log(f"Error loading JSON: {e}")
        
    def _update_graph_vis(self):
        self.ax.clear()
        depot_node = self.customers[0]
        customer_nodes = self.customers[1:]
        neighbours = 5
        edges_drawn = set()
        for i in range(len(self.customers)):
            distances_from_i = self.distance_matrix[i].copy()
            distances_from_i[i] = np.inf
            nearest_indices = np.argsort(distances_from_i)[:neighbours]
            for j in nearest_indices:
                if i < j: ## Ensure that the edge is drawn once
                    edge_key = (i, j)
                    if edge_key not in edges_drawn:
                        customer_i = self.customers[i]
                        customer_j = self.customers[j]
                        distance = self.distance_matrix[i][j]

                        alpha = 0.3 ## Determine each edge and add a distance label
                        self.ax.plot([customer_i.x, customer_j.x], [customer_i.y, customer_j.y], 'gray', alpha = alpha, linewidth = 1)
                        mid_x = (customer_i.x + customer_j.x) / 2
                        mid_y = (customer_i.y + customer_j.y) / 2
                        self.ax.text(mid_x, mid_y, f'{distance:.0f}')
                        edges_drawn.add(edge_key)

        self.ax.scatter(depot_node.x, depot_node.y, s = 200, c = 'red', marker = 's', label = "Depot", edgecolors = 'darkred', linewidth = 2) ## Plot Depot
        self.ax.text(depot_node.x, depot_node.y - 3, 'Depot', fontweight = 'bold')

        if customer_nodes:       ## Plot Customers
            customer_x = [node.x for node in customer_nodes]
            customer_y = [node.y for node in customer_nodes]
            demands = [node.demand for node in customer_nodes]
            self.ax.scatter(customer_x, customer_y, s = 200, c = demands, label = 'Customers', edgecolors = 'black', linewidth = 1)
            for node in customer_nodes:
                self.ax.text(node.x, node.y - 3, f'C{node.id}', fontweight = 'bold')

        if self.current_route: ## Deviation from graph creation: Algorithm path displayer
            for index in range(len(self.current_route) - 1):
                customer_from = self.nodes[self.current_route[index]]
                customer_to = self.ax.plot([self.current_route[index + 1]])
                self.ax.plot([customer_from.x, customer_to.x], [customer_from.y, customer_to.y], 'b-', linewidth = 2, alpha = 0.5)
            
        self.ax.set_title(f"VRP Graph ({len(self.customers)-1} customers)", fontweight = 'bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _update_info(self):
        self.info_text.config(state = tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        info = f"Graph information\nTotal customers: {len(self.customers)-1}\nTotal depots: 1\n"
        total_demand = sum(node.demand for node in self.customers[1:])
        info += f"Total Demand: {total_demand}\n"
        if self.current_route:
            info += f"Current route:"
            route_str = " -> ".join(str(node_id) for node_id in self.current_route)
            info += f"{route_str}\nTotal Distance: {self.total_distance:.1f}\n"
        self.info_text.insert(tk.END, info)
        self.info_text.config(state = tk.DISABLED)

    def _add_log(self, message):
        self.log_text.config(state = tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state = tk.DISABLED)
        self.root.update()
    
    def _run_algorithm(self, algorithm_name): ## Ensures graph generated then runs selected algorithm
        if self.customers is None:
            messagebox.showwarning("Warning", "Generate graph first")
            return
        self.log_text.config(state = tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state = tk.DISABLED)
        if algorithm_name == "simple":
            self._brute_force()
        elif algorithm_name == "complex":
            self._savings_clarke_wright()
        elif algorithm_name == "ai":
            self._local_search()
        
    def _brute_force(self): ## Brute force - greedy algorithm - starts at depot and visits closest unvisited customer before returning
        self._add_log("Brute force algorithm")
        self._add_log("Greedy algorithm that starts at depot and visits closest unvisited customer")
        self.current_route = [0]
        unvisited = set(range(1,len(self.customers)))
        current_node = 0
        total_distance = 0
        self._add_log(f"Start at depot (Node 0)")
        time.sleep(0.5)
        step = 2
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
            self._add_log(f"Step {step}: Move to Node {nearest_node} (dist: {nearest_distance:.1f})")
            self._add_log(f"Unvisited: {sorted(unvisited) if unvisited else "None"}")
            current_node = nearest_node
            step += 1
            self._update_graph_vis()
            time.sleep(0.3)
        ################################### Add check to vehicle capacity to have it return and start again##############################################################
        return_distance = self.distance_matrix[current_node][0]
        self.current_route.append(0)
        total_distance += return_distance
        self._add_log(f"Step {step}: Return to Depot (dist: {return_distance:.1f})")

        self.total_distance = total_distance
        self._add_log(f"Route: {' -> '.join(map(str,self.current_route))}")
        self._add_log(f"Total distance: {self.total_distance:.1f}")
        self._update_graph_vis()
        self._update_info()
    
    def _savings_clarke_wright(self):
        self._add_log("Savings or Clarke-wright algorithm")
        self._add_log("Combines routes together, merging the most beneficial pairs first")
        self._add_log("Step 1: calculate savings for every node pair")
        savings_list = []
        for i in range(1, len(self.customers)):
            for j in range(i + 1, len(self.customers)):
                potential_saving = (self.distance_matrix[0][i] + self.distance_matrix[0][j] - self.distance_matrix[i][j])
                potential_saving.append((potential_saving, i, j))
        savings_list.sort(reverse = True)
        self._add_log(f"Potential pairs: {len(savings_list)} e.g.")
        for index, (potential_saving, i, j) in enumerate(savings_list[:5]): ## List potential 
            self._add_log(f"{index+1}. Customer {i} - {j}: {potential_saving:.1f}")
        routes = [[i] for i in range(1, len(self.customers))]

        self._add_log(f"\nStep 2: merge routes based on savings")
        pairs_merged = 0
        for potential_saving, i, j in savings_list:
            route_i = None
            route_j = None
            for route in routes:
                if i in route:
                    route_i = route
                if j in route:
                    route_j = route
            if route_i and route_j and route_i != route_j:
                if route_i[-1] == i and route_j[0] == j:
                    routes.remove(route_i)
                    routes.remove(route_j)
                    routes.append(route_i + route_j)
                    pairs_merged += 1
                    self._add_log(f"Merged: {route_i} + {route_j}")

        self.current_route = [0] ## Convert into single route to display
        total_distance = 0
        for route in routes:
            for node in route:
                self.current_route.append(node)
                if len(self.current_route) > 1:
                    total_distance += self.distance_matrix[self.current_route[-2]][node]
        self.current_route.append(0)
        total_distance += self.distance_matrix[self.current_route[-2]][0]
        self.total_distance = total_distance

        self._add_log(f"Routes merged: {pairs_merged}")
        self._add_log(f"Route: {' -> '.join(map(str, self.current_route))}")
        self._add_log(f"Total distance: {self.total_distance:.1f}")

        self._update_graph_vis()
        self._update_info()
    
    def _local_search(self):
        self._add_log("Local search or two-opt improvement algorithm")
        self._add_log("Improve the route to the nearest neighbour in reverse by exploring paths away")
        self._add_log("Step 1: Inital route creation - recommended brute force")
        self.current_route = [0]
        unvisited = set(range(1,len(self.customers)))
        current_node = 0
        total_distance = 0
        self._add_log(f"START AT DEPOT (Node 0)")
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
            self._add_log(f"Unvisited: {sorted(unvisited) if unvisited else "None"}")
            current_node = nearest_node
        ################################### Add check to vehicle capacity to have it return and start again##############################################################
        return_distance = self.distance_matrix[current_node][0]
        self.current_route.append(0)
        total_distance += return_distance
        self._update_graph_vis()

        self._add_log(f"\nStep 2: Apply 2-Opt improvement")
        improved = True
        iteration = 0
        best_distance = total_distance
        while improved and iteration < 20:
            improved = False
            iteration += 1
            for i in range(1, len(self.current_route) - 2):
                for j in range(i + 2, len(self.current_route)):
                    a, b = self.current_route[i-1], self.current_route[i]
                    c, d = self.current_route[j-1], self.current_route[j]

                    old_distance = self.distance_matrix[a][b] + self.distance_matrix[c][d]
                    new_distance = self.distance_matrix[a][c] + self.distance_matrix[b][d]

                    if new_distance < old_distance: ## Reroute to new route if better than previous route
                        self.current_route[i:j] = self.current_route[i:j][::-1]
                        best_distance -= (old_distance - new_distance)
                        improved = True
                        self._add_log(f"Iteration {iteration}: New distancce: {best_distance:.1f}")
                        self._update_graph_vis()
                        break
                if improved:
                    break
        self.total_distance = best_distance
        self._add_log(f"Iterations completed: {iteration}")
        self._add_log(f"Route: {' -> '.join(map(str, self.current_route))}")
        self._add_log(f"Distance travelled: {self.total_distance:.1f}")
        self._update_graph_vis()
        self._update_info()
   
def main():
    root = tk.Tk()
    app = VRPSolver(root)
    root.mainloop()

if __name__ == "__main__":
    main()
