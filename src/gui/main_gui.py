"""Main GUI application for the distributed system."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
from typing import Dict, List, Optional, Any
import random
import logging

# Try to import colorama for colored text
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# Import system components
# Note: These imports are for reference - the GUI works standalone for demonstration
try:
    from ..common.messages import Message, MessageType
except ImportError:
    # Fallback for standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class DistributedSystemGUI:
    """Main GUI application for the distributed system."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Carrier-Grade Edge-Core-Cloud Distributed System")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")
        
        # System state
        self.nodes = {
            "edge": [],
            "core": [],
            "cloud": []
        }
        self.transactions = []
        self.metrics_history = []
        self.running = False
        
        # Colors
        self.colors = {
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "edge": "#4a9eff",
            "core": "#ff6b6b",
            "cloud": "#51cf66",
            "success": "#51cf66",
            "error": "#ff6b6b",
            "warning": "#ffd43b",
            "text": "#ffffff"
        }
        
        # Setup GUI
        self._setup_gui()
        
        # Start update loop
        self.update_interval = 1000  # ms
        self.update_metrics()
        
        # Load sample configuration
        self._load_sample_config()
    
    def _setup_gui(self):
        """Setup the GUI components."""
        # Create main container
        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame: Title and controls
        top_frame = tk.Frame(main_container, bg=self.colors["bg"])
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            top_frame,
            text="Carrier-Grade Edge-Core-Cloud Distributed System",
            font=("Arial", 16, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Control buttons
        control_frame = tk.Frame(top_frame, bg=self.colors["bg"])
        control_frame.pack(side=tk.RIGHT)
        
        self.start_btn = tk.Button(
            control_frame,
            text="Start System",
            command=self.start_system,
            bg="#51cf66",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="Stop System",
            command=self.stop_system,
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content area
        content_frame = tk.Frame(main_container, bg=self.colors["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel: System topology and controls
        left_panel = tk.Frame(content_frame, bg=self.colors["bg"], width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # System topology
        topology_frame = tk.LabelFrame(
            left_panel,
            text="System Topology",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11, "bold")
        )
        topology_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.topology_canvas = tk.Canvas(
            topology_frame,
            bg=self.colors["bg"],
            highlightthickness=0
        )
        self.topology_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Transaction controls
        transaction_frame = tk.LabelFrame(
            left_panel,
            text="Transaction Controls",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11, "bold")
        )
        transaction_frame.pack(fill=tk.X, pady=(0, 10))
        
        txn_control_frame = tk.Frame(transaction_frame, bg=self.colors["bg"])
        txn_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.execute_txn_btn = tk.Button(
            txn_control_frame,
            text="Execute Transaction",
            command=self.execute_transaction,
            bg="#4a9eff",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        self.execute_txn_btn.pack(side=tk.LEFT, padx=5)
        
        self.abort_txn_btn = tk.Button(
            txn_control_frame,
            text="Abort Transaction",
            command=self.abort_transaction,
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        self.abort_txn_btn.pack(side=tk.LEFT, padx=5)
        
        # Fault injection
        fault_frame = tk.LabelFrame(
            left_panel,
            text="Fault Injection",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11, "bold")
        )
        fault_frame.pack(fill=tk.X)
        
        fault_control_frame = tk.Frame(fault_frame, bg=self.colors["bg"])
        fault_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.inject_fault_btn = tk.Button(
            fault_control_frame,
            text="Inject Node Failure",
            command=self.inject_fault,
            bg="#ffd43b",
            fg="black",
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        self.inject_fault_btn.pack(side=tk.LEFT, padx=5)
        
        # Right panel: Metrics and logs
        right_panel = tk.Frame(content_frame, bg=self.colors["bg"])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Metrics display
        metrics_frame = tk.LabelFrame(
            right_panel,
            text="System Metrics",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11, "bold")
        )
        metrics_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.metrics_text = scrolledtext.ScrolledText(
            metrics_frame,
            bg="#2d2d2d",
            fg=self.colors["fg"],
            font=("Courier", 9),
            wrap=tk.WORD
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Transaction log
        log_frame = tk.LabelFrame(
            right_panel,
            text="Transaction Log",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11, "bold")
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg="#2d2d2d",
            fg=self.colors["fg"],
            font=("Courier", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Draw initial topology
        self._draw_topology()
    
    def _load_sample_config(self):
        """Load sample configuration."""
        self.sample_config = {
            "edge_nodes": [
                {"node_id": "edge-1", "host": "localhost", "port": 8001},
                {"node_id": "edge-2", "host": "localhost", "port": 8002},
                {"node_id": "edge-3", "host": "localhost", "port": 8003}
            ],
            "core_nodes": [
                {"node_id": "core-1", "host": "localhost", "port": 9001},
                {"node_id": "core-2", "host": "localhost", "port": 9002}
            ],
            "cloud_nodes": [
                {"node_id": "cloud-1", "host": "localhost", "port": 10001},
                {"node_id": "cloud-2", "host": "localhost", "port": 10002}
            ]
        }
    
    def _draw_topology(self):
        """Draw the system topology."""
        self.topology_canvas.delete("all")
        
        width = self.topology_canvas.winfo_width()
        height = self.topology_canvas.winfo_height()
        
        if width < 10 or height < 10:
            return
        
        # Draw edge nodes
        edge_y = height * 0.2
        edge_spacing = width / 4
        for i, node in enumerate(self.sample_config["edge_nodes"]):
            x = edge_spacing * (i + 1)
            color = self.colors["edge"]
            self.topology_canvas.create_oval(
                x - 20, edge_y - 20,
                x + 20, edge_y + 20,
                fill=color,
                outline="white",
                width=2,
                tags=("node", node["node_id"])
            )
            self.topology_canvas.create_text(
                x, edge_y - 35,
                text=node["node_id"],
                fill="white",
                font=("Arial", 8)
            )
        
        # Draw core nodes
        core_y = height * 0.5
        core_spacing = width / 3
        for i, node in enumerate(self.sample_config["core_nodes"]):
            x = core_spacing * (i + 1)
            color = self.colors["core"]
            self.topology_canvas.create_oval(
                x - 25, core_y - 25,
                x + 25, core_y + 25,
                fill=color,
                outline="white",
                width=2,
                tags=("node", node["node_id"])
            )
            self.topology_canvas.create_text(
                x, core_y - 40,
                text=node["node_id"],
                fill="white",
                font=("Arial", 8, "bold")
            )
        
        # Draw cloud nodes
        cloud_y = height * 0.8
        cloud_spacing = width / 3
        for i, node in enumerate(self.sample_config["cloud_nodes"]):
            x = cloud_spacing * (i + 1)
            color = self.colors["cloud"]
            self.topology_canvas.create_rectangle(
                x - 30, cloud_y - 20,
                x + 30, cloud_y + 20,
                fill=color,
                outline="white",
                width=2,
                tags=("node", node["node_id"])
            )
            self.topology_canvas.create_text(
                x, cloud_y - 35,
                text=node["node_id"],
                fill="white",
                font=("Arial", 8)
            )
        
        # Draw connections
        # Edge to Core
        for i in range(3):
            edge_x = edge_spacing * (i + 1)
            for j in range(2):
                core_x = core_spacing * (j + 1)
                self.topology_canvas.create_line(
                    edge_x, edge_y + 20,
                    core_x, core_y - 25,
                    fill="gray",
                    width=1,
                    dash=(5, 5)
                )
        
        # Core to Cloud
        for i in range(2):
            core_x = core_spacing * (i + 1)
            for j in range(2):
                cloud_x = cloud_spacing * (j + 1)
                self.topology_canvas.create_line(
                    core_x, core_y + 25,
                    cloud_x, cloud_y - 20,
                    fill="gray",
                    width=1,
                    dash=(5, 5)
                )
    
    def start_system(self):
        """Start the distributed system."""
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log("System started", "info")
        self._draw_topology()
    
    def stop_system(self):
        """Stop the distributed system."""
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log("System stopped", "info")
    
    def execute_transaction(self):
        """Execute a sample transaction."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        transaction_id = f"TXN-{int(time.time())}"
        self.log(f"Executing transaction: {transaction_id}", "info")
        
        # Simulate transaction execution
        self.log(f"Phase 1: PREPARE sent to participants", "info")
        time.sleep(0.5)
        self.log(f"Phase 1: All participants voted COMMIT", "success")
        time.sleep(0.5)
        self.log(f"Phase 2: COMMIT sent to participants", "info")
        time.sleep(0.5)
        self.log(f"Transaction {transaction_id} COMMITTED successfully", "success")
        
        self.transactions.append({
            "id": transaction_id,
            "status": "COMMITTED",
            "timestamp": time.time()
        })
    
    def abort_transaction(self):
        """Abort a transaction."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        transaction_id = f"TXN-{int(time.time())}"
        self.log(f"Aborting transaction: {transaction_id}", "warning")
        self.log(f"Phase 1: PREPARE sent to participants", "info")
        time.sleep(0.5)
        self.log(f"Phase 1: Participant voted ABORT", "error")
        time.sleep(0.5)
        self.log(f"Phase 2: ABORT sent to participants", "info")
        time.sleep(0.5)
        self.log(f"Transaction {transaction_id} ABORTED", "error")
    
    def inject_fault(self):
        """Inject a node failure."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        # Select random node
        all_nodes = (
            self.sample_config["edge_nodes"] +
            self.sample_config["core_nodes"] +
            self.sample_config["cloud_nodes"]
        )
        node = random.choice(all_nodes)
        
        self.log(f"Injecting failure in node: {node['node_id']}", "warning")
        time.sleep(0.5)
        self.log(f"Node {node['node_id']} failed", "error")
        time.sleep(0.5)
        self.log(f"Failover triggered, replacement node selected", "info")
        time.sleep(0.5)
        self.log(f"System recovered", "success")
    
    def update_metrics(self):
        """Update system metrics display."""
        if self.running:
            metrics = {
                "Timestamp": time.strftime("%H:%M:%S"),
                "Edge Nodes": len(self.sample_config["edge_nodes"]),
                "Core Nodes": len(self.sample_config["core_nodes"]),
                "Cloud Nodes": len(self.sample_config["cloud_nodes"]),
                "Active Transactions": len([t for t in self.transactions if t.get("status") == "COMMITTED"]),
                "CPU Usage": f"{random.uniform(20, 80):.1f}%",
                "Memory Usage": f"{random.uniform(30, 70):.1f}%",
                "Network Latency": f"{random.uniform(5, 50):.1f}ms",
                "Throughput": f"{random.uniform(1000, 10000):.0f} req/s"
            }
            
            self.metrics_text.delete(1.0, tk.END)
            for key, value in metrics.items():
                self.metrics_text.insert(tk.END, f"{key:20s}: {value}\n", "metrics")
        
        self.root.after(self.update_interval, self.update_metrics)
    
    def log(self, message: str, level: str = "info"):
        """Add a log entry."""
        timestamp = time.strftime("%H:%M:%S")
        tag = f"log_{level}"
        
        color_map = {
            "info": "#4a9eff",
            "success": "#51cf66",
            "error": "#ff6b6b",
            "warning": "#ffd43b"
        }
        
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        
        # Configure tag colors
        self.log_text.tag_config(tag, foreground=color_map.get(level, "#ffffff"))


def main():
    """Main function."""
    root = tk.Tk()
    app = DistributedSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
