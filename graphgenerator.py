import random
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class CustomerNode:
    id: int
    x: float
    y: float
    demand: int = 0
    is_depot: bool = False

class GraphGenerator:
    def __init__(self, num_customers: int = 20, graph_id: int = 1, grid_size: int = 100): ## Establish key variable values
        
        self.num_customers = num_customers
        self.grid_size = grid_size
        self.customers = []
        self.distance_matrix = []
        if graph_id != None:
            random.seed(graph_id)
            np.random.seed(graph_id)
        
    def generate_graph(self): ## Does not display but creates a graph
        self.customers = []
        depot = CustomerNode(id = 0, x = self.grid_size/2, y = self.grid_size/2, is_depot = True)
        self.customers.append(depot)
        customers_created = 0
        attempts = 0
        while customers_created < self.num_customers and attempts < 1000: ## Attempts prevent infinite loop if the graph isn't as spacious
            too_close = False
            x = random.randint(0, self.grid_size)
            y = random.randint(0, self.grid_size)
            
            for existing_customer in self.customers: ## Checks if the nodes are too close together for greater readability
                distance = np.sqrt((x - existing_customer.x)**2 + (y - existing_customer.y)**2) ## Pythagoras applied to determine actual distance between nodes
                if distance < 5:
                    too_close = True
                    break
                    
            if too_close == False:
                customer = CustomerNode(id = customers_created + 1, x = x, y = y, demand = random.randint(1, 20), is_depot = False) ## New customer recorded where node can be made
                attempts += 1
            if customers_created < self.num_customers:
                ## Produce message that customers could not fit on the size of the graph
                raise ValueError("Insufficient graph space")
            self.calculate_distances()
            return self.customers, self.distance_matrix
            
    def calculate_distances(self): ## Fills in distance matrix with every nodes distance from one another
        customers_count = len(self.customers)
        self.distance_matrix = np.zeros((customers_count,customers_count))
        for i in range(customers_count):
            for j in range(customers_count):
                if i != j:
                    customer_i = self.customers[i]
                    customer_j = self.customers[j]
                    distance = np.sqrt((customer_i.x - customer_j.x)**2 + (customer_i.y - customer_j.y)**2)
                    self.distance_matrix[i][j] = distance
        print(self.distance_matrix)

    def display_graph(self, figsize: Tuple[int,int] = (12, 10), show_edge: bool = True, show_demand: bool = True, neighbours: int = 5):
        fig, ax = plt.subplots(figsize = figsize) ## figure, axes and node types established
        depot_node = self.customers[0]
        customer_nodes = self.customers[1:]
        if show_edge > 1 and len(self.customers) > 1:
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
                            mid_x = (customer_i.x + customer_j.x) / 2 ## Determine the middle of each edge and add the distance label
                            mid_y = (customer_i.y + customer_j.y) / 2
                            ax.text(mid_x, mid_y, f'{distance:.0f}')
                            edges_drawn.add(edge_key)
        ax.scatter(depot_node.x, depot_node.y, s = 200, c = 'red', marker = 's', label = 'Depot', edgecolors = 'darkred', linewidth = 2) ## Plot Depot
        ax.text(depot_node.x, depot_node.y - 3, 'Depot', fontweight = 'bold')
        if customer_nodes:       ## Plot customers
            customer_x = [node.x for node in customer_nodes]
            customer_y = [node.y for node in customer_nodes]
            demands = [node.demand for node in customer_nodes]
            scatter = ax.scatter(customer_x, customer_y, s = 200, c = demands, label = 'Customers', edgecolors = 'black', linewidth = 1)
            for node in customer_nodes:
                ax.text(node.x, node.y - 3, f'{node.id}', fontweight = 'bold')
                if show_demand:
                    ax.text(node.x, node.y + 3, f'd={node.demand}')
        ax.set_title(f'VRP graph\n({self.num_customers} customers)', fontweight = 'bold')
        ax.set_xlim(-5, self.grid_size + 5) ## Set axis limits and grid
        ax.set_ylim(-5, self.grid_size + 5)
        ax.legend(loc = 'upper right')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        plt.tight_layout()
        return fig, ax

    def graph_info(self):
        print(f"VRP Graph info: {len(self.customers)} \nCustomers: {len(self.customers) - 1}")
        for node in self.nodes:
            if node.is_Depot == True:
                node_type = "Depot"
            else:
                node_type = "Customer"
            print(f"{node.id} - {node_type} - {node.x},{node.y} -> {node.demand}")
        print(f"\nTotal demand: {sum(node.demand for node in self.customers[1:])}")

def main():
    print("Generating random VRP graph...")
    generator = GraphGenerator(num_customers=25, grid_size=100, graph_id = 42)
    nodes, distance_matrix = generator.generate_graph()
    generator.graph_info()
    fig, ax = generator.display_graph(figsize = (14, 10), show_edge = True, show_demand = True)
    plt.show()

if __name__ == "__main__":
    main()
