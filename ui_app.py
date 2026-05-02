import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
import os
from graphgenerator import GraphGenerator, CustomerNode
import numpy as np

class VRPGraphUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VRP Graph Visualizer")
        self.root.geometry("1200x700")
        self.generator = None
        self.canvas = None
        self.canvas_widget = None
        
        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create control panel
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Create button to load JSON
        self.load_button = tk.Button(
            self.control_frame,
            text="Load VRP Graph from JSON",
            command=self.load_json_file,
            font=("Arial", 12),
            padx=20,
            pady=10,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        # Create status label
        self.status_label = tk.Label(
            self.control_frame,
            text="No graph loaded",
            font=("Arial", 10),
            fg="gray"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Create canvas frame for graph display
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def load_json_file(self):
        """Load JSON file and create VRP graph"""
        file_path = filedialog.askopenfilename(
            title="Select VRP Graph JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Create generator and load graph from JSON
            self.load_graph_from_json(data, file_path)
            
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON file format")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")
    
    def load_graph_from_json(self, data, file_path):
        """Load graph data from JSON and display it"""
        try:
            # Extract graph parameters
            num_customers = len(data.get("customers", []))
            grid_size = data.get("grid_size", 100)
            
            # Create generator
            self.generator = GraphGenerator(
                num_customers=num_customers,
                grid_size=grid_size,
                graph_id=None
            )
            
            # Load customers from JSON
            self.generator.customers = []
            
            # Add depot
            depot_data = data.get("depot", {"id": 0, "x": grid_size/2, "y": grid_size/2})
            depot = CustomerNode(
                id=depot_data.get("id", 0),
                x=depot_data.get("x", grid_size/2),
                y=depot_data.get("y", grid_size/2),
                demand=depot_data.get("demand", 0),
                is_depot=True
            )
            self.generator.customers.append(depot)
            
            # Add customers
            for customer_data in data.get("customers", []):
                customer = CustomerNode(
                    id=customer_data.get("id", 0),
                    x=customer_data.get("x", 0),
                    y=customer_data.get("y", 0),
                    demand=customer_data.get("demand", 0),
                    is_depot=False
                )
                self.generator.customers.append(customer)
            
            # Calculate distance matrix
            self.generator.calculate_distances()
            
            # Display the graph
            self.display_graph()
            
            # Update status
            file_name = os.path.basename(file_path)
            self.status_label.config(
                text=f"Loaded: {file_name} | Customers: {num_customers}",
                fg="green"
            )
            
        except KeyError as e:
            messagebox.showerror("Error", f"Missing required field in JSON: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading graph: {str(e)}")
    
    def display_graph(self):
        """Display the VRP graph on the canvas"""
        if self.generator is None or not self.generator.customers:
            messagebox.showwarning("Warning", "No graph to display")
            return
        
        # Clear previous canvas
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
        
        # Create figure using generator's display_graph method
        fig, ax = self.generator.display_graph(figsize=(12, 8))
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas_widget = self.canvas
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def main():
    root = tk.Tk()
    app = VRPGraphUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
