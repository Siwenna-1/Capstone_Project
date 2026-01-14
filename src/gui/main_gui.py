"""Enhanced GUI application for the distributed system with comprehensive demonstrations."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
from typing import Dict, List, Optional, Any
import random
import logging

# Helper function to dim colors (simulate 50% opacity)
def dim_color(color_hex: str, opacity: float = 0.5) -> str:
    """Dim a hex color to simulate opacity."""
    # Convert hex to RGB
    color_hex = color_hex.lstrip('#')
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    
    # Blend with dark background (50% of original)
    r = int(r * opacity)
    g = int(g * opacity)
    b = int(b * opacity)
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"


class DistributedSystemGUI:
    """Enhanced GUI application for the distributed system."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Carrier-Grade Edge-Core-Cloud Distributed System - Enhanced")
        self.root.geometry("1600x1000")
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
        
        # Node states (True = up, False = down)
        self.node_states: Dict[str, bool] = {}
        
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
            "text": "#ffffff",
            "dimmed": "#666666"  # Gray for dimmed nodes
        }
        
        # Demonstration delays (longer for presentations - 2-3 seconds)
        self.delay_short = 1.5  # Short delay
        self.delay_medium = 2.5  # Medium delay
        self.delay_long = 3.0  # Long delay
        
        # Setup GUI
        self._setup_gui()
        
        # Start update loop
        self.update_interval = 1000  # ms
        self.update_metrics()
        
        # Load sample configuration
        self._load_sample_config()
        
        # Initialize node states (all up initially)
        self._initialize_node_states()
    
    def _initialize_node_states(self):
        """Initialize all nodes as up."""
        for node in self.sample_config["edge_nodes"]:
            self.node_states[node["node_id"]] = True
        for node in self.sample_config["core_nodes"]:
            self.node_states[node["node_id"]] = True
        for node in self.sample_config["cloud_nodes"]:
            self.node_states[node["node_id"]] = True
    
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
        
        self.clear_logs_btn = tk.Button(
            control_frame,
            text="Clear Logs",
            command=self.clear_logs,
            bg="#666666",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        self.clear_logs_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content area
        content_frame = tk.Frame(main_container, bg=self.colors["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel: System topology and controls
        left_panel = tk.Frame(content_frame, bg=self.colors["bg"], width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # System topology
        topology_frame = tk.LabelFrame(
            left_panel,
            text="System Topology (Click nodes to see details)",
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
        
        # Bind canvas resize
        self.topology_canvas.bind('<Configure>', lambda e: self._draw_topology())
        
        # Demonstration controls
        demo_frame = tk.LabelFrame(
            left_panel,
            text="Demonstrations",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Arial", 11, "bold")
        )
        demo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        demo_notebook = ttk.Notebook(demo_frame)
        demo_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Transactions tab
        txn_frame = tk.Frame(demo_notebook, bg=self.colors["bg"])
        demo_notebook.add(txn_frame, text="Transactions")
        
        self.execute_txn_btn = tk.Button(
            txn_frame,
            text="Execute Transaction (2PC)",
            command=self.execute_transaction,
            bg="#4a9eff",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.execute_txn_btn.pack(pady=5)
        
        self.abort_txn_btn = tk.Button(
            txn_frame,
            text="Abort Transaction",
            command=self.abort_transaction,
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.abort_txn_btn.pack(pady=5)
        
        # Communication tab
        comm_frame = tk.Frame(demo_notebook, bg=self.colors["bg"])
        demo_notebook.add(comm_frame, text="Communication")
        
        self.demo_rpc_btn = tk.Button(
            comm_frame,
            text="Demonstrate RPC",
            command=self.demonstrate_rpc,
            bg="#4a9eff",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.demo_rpc_btn.pack(pady=5)
        
        self.demo_messaging_btn = tk.Button(
            comm_frame,
            text="Demonstrate Messaging",
            command=self.demonstrate_messaging,
            bg="#4a9eff",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.demo_messaging_btn.pack(pady=5)
        
        # DSM tab
        dsm_frame = tk.Frame(demo_notebook, bg=self.colors["bg"])
        demo_notebook.add(dsm_frame, text="DSM")
        
        self.demo_dsm_btn = tk.Button(
            dsm_frame,
            text="Demonstrate DSM",
            command=self.demonstrate_dsm,
            bg="#51cf66",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.demo_dsm_btn.pack(pady=5)
        
        # Event Ordering tab
        event_frame = tk.Frame(demo_notebook, bg=self.colors["bg"])
        demo_notebook.add(event_frame, text="Event Ordering")
        
        self.demo_event_btn = tk.Button(
            event_frame,
            text="Demonstrate Event Ordering",
            command=self.demonstrate_event_ordering,
            bg="#51cf66",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.demo_event_btn.pack(pady=5)
        
        # Replication tab
        repl_frame = tk.Frame(demo_notebook, bg=self.colors["bg"])
        demo_notebook.add(repl_frame, text="Replication")
        
        self.demo_replication_btn = tk.Button(
            repl_frame,
            text="Demonstrate Replication",
            command=self.demonstrate_replication,
            bg="#51cf66",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.demo_replication_btn.pack(pady=5)
        
        # Fault Tolerance tab
        fault_frame = tk.Frame(demo_notebook, bg=self.colors["bg"])
        demo_notebook.add(fault_frame, text="Fault Tolerance")
        
        self.inject_fault_btn = tk.Button(
            fault_frame,
            text="Inject Node Failure",
            command=self.inject_fault,
            bg="#ffd43b",
            fg="black",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.inject_fault_btn.pack(pady=5)
        
        self.recover_node_btn = tk.Button(
            fault_frame,
            text="Recover All Nodes",
            command=self.recover_all_nodes,
            bg="#51cf66",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.recover_node_btn.pack(pady=5)
        
        # Load Balancing tab
        load_frame = tk.Frame(demo_notebook, bg=self.colors["bg"])
        demo_notebook.add(load_frame, text="Load Balancing")
        
        self.demo_load_balancing_btn = tk.Button(
            load_frame,
            text="Demonstrate Load Balancing",
            command=self.demonstrate_load_balancing,
            bg="#ffd43b",
            fg="black",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.demo_load_balancing_btn.pack(pady=5)
        
        # Migration tab
        mig_frame = tk.Frame(demo_notebook, bg=self.colors["bg"])
        demo_notebook.add(mig_frame, text="Migration")
        
        self.demo_migration_btn = tk.Button(
            mig_frame,
            text="Demonstrate Migration",
            command=self.demonstrate_migration,
            bg="#ffd43b",
            fg="black",
            font=("Arial", 9),
            padx=10,
            pady=8,
            width=25
        )
        self.demo_migration_btn.pack(pady=5)
        
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
            text="System Logs (All Events)",
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
        
        # Configure log text tags
        self.log_text.tag_config("log_info", foreground="#4a9eff")
        self.log_text.tag_config("log_success", foreground="#51cf66")
        self.log_text.tag_config("log_error", foreground="#ff6b6b")
        self.log_text.tag_config("log_warning", foreground="#ffd43b")
        self.log_text.tag_config("log_section", foreground="#ffffff", font=("Courier", 9, "bold"))
        
        # Draw initial topology
        self.root.update()
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
        """Draw the system topology with node states."""
        self.topology_canvas.delete("all")
        
        width = self.topology_canvas.winfo_width()
        height = self.topology_canvas.winfo_height()
        
        if width < 10 or height < 10:
            return
        
        # Draw edge nodes
        edge_y = height * 0.15
        edge_spacing = width / 4
        for i, node in enumerate(self.sample_config["edge_nodes"]):
            x = edge_spacing * (i + 1)
            node_id = node["node_id"]
            is_up = self.node_states.get(node_id, True)
            
            # Use dimmed color if node is down
            if is_up:
                fill_color = self.colors["edge"]
                outline_color = "white"
            else:
                fill_color = dim_color(self.colors["edge"], 0.5)
                outline_color = "#888888"
            
            self.topology_canvas.create_oval(
                x - 22, edge_y - 22,
                x + 22, edge_y + 22,
                fill=fill_color,
                outline=outline_color,
                width=2,
                tags=("node", node_id, "edge")
            )
            self.topology_canvas.create_text(
                x, edge_y - 40,
                text=node_id,
                fill=outline_color,
                font=("Arial", 8)
            )
            # Status indicator
            status_text = "UP" if is_up else "DOWN"
            status_color = "#51cf66" if is_up else "#ff6b6b"
            self.topology_canvas.create_text(
                x, edge_y + 35,
                text=status_text,
                fill=status_color,
                font=("Arial", 7, "bold")
            )
        
        # Draw core nodes
        core_y = height * 0.5
        core_spacing = width / 3
        for i, node in enumerate(self.sample_config["core_nodes"]):
            x = core_spacing * (i + 1)
            node_id = node["node_id"]
            is_up = self.node_states.get(node_id, True)
            
            if is_up:
                fill_color = self.colors["core"]
                outline_color = "white"
            else:
                fill_color = dim_color(self.colors["core"], 0.5)
                outline_color = "#888888"
            
            self.topology_canvas.create_oval(
                x - 27, core_y - 27,
                x + 27, core_y + 27,
                fill=fill_color,
                outline=outline_color,
                width=2,
                tags=("node", node_id, "core")
            )
            self.topology_canvas.create_text(
                x, core_y - 45,
                text=node_id,
                fill=outline_color,
                font=("Arial", 8, "bold")
            )
            status_text = "UP" if is_up else "DOWN"
            status_color = "#51cf66" if is_up else "#ff6b6b"
            self.topology_canvas.create_text(
                x, core_y + 42,
                text=status_text,
                fill=status_color,
                font=("Arial", 7, "bold")
            )
        
        # Draw cloud nodes
        cloud_y = height * 0.85
        cloud_spacing = width / 3
        for i, node in enumerate(self.sample_config["cloud_nodes"]):
            x = cloud_spacing * (i + 1)
            node_id = node["node_id"]
            is_up = self.node_states.get(node_id, True)
            
            if is_up:
                fill_color = self.colors["cloud"]
                outline_color = "white"
            else:
                fill_color = dim_color(self.colors["cloud"], 0.5)
                outline_color = "#888888"
            
            self.topology_canvas.create_rectangle(
                x - 32, cloud_y - 22,
                x + 32, cloud_y + 22,
                fill=fill_color,
                outline=outline_color,
                width=2,
                tags=("node", node_id, "cloud")
            )
            self.topology_canvas.create_text(
                x, cloud_y - 40,
                text=node_id,
                fill=outline_color,
                font=("Arial", 8)
            )
            status_text = "UP" if is_up else "DOWN"
            status_color = "#51cf66" if is_up else "#ff6b6b"
            self.topology_canvas.create_text(
                x, cloud_y + 35,
                text=status_text,
                fill=status_color,
                font=("Arial", 7, "bold")
            )
        
        # Draw connections (only between up nodes)
        # Edge to Core
        for i, edge_node in enumerate(self.sample_config["edge_nodes"]):
            edge_x = edge_spacing * (i + 1)
            edge_id = edge_node["node_id"]
            if not self.node_states.get(edge_id, True):
                continue
                
            for j, core_node in enumerate(self.sample_config["core_nodes"]):
                core_x = core_spacing * (j + 1)
                core_id = core_node["node_id"]
                if not self.node_states.get(core_id, True):
                    continue
                    
                self.topology_canvas.create_line(
                    edge_x, edge_y + 22,
                    core_x, core_y - 27,
                    fill="#666666",
                    width=1,
                    dash=(5, 5)
                )
        
        # Core to Cloud
        for i, core_node in enumerate(self.sample_config["core_nodes"]):
            core_x = core_spacing * (i + 1)
            core_id = core_node["node_id"]
            if not self.node_states.get(core_id, True):
                continue
                
            for j, cloud_node in enumerate(self.sample_config["cloud_nodes"]):
                cloud_x = cloud_spacing * (j + 1)
                cloud_id = cloud_node["node_id"]
                if not self.node_states.get(cloud_id, True):
                    continue
                    
                self.topology_canvas.create_line(
                    core_x, core_y + 27,
                    cloud_x, cloud_y - 22,
                    fill="#666666",
                    width=1,
                    dash=(5, 5)
                )
    
    def start_system(self):
        """Start the distributed system."""
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log_section("SYSTEM INITIALIZATION")
        self.log("System starting...", "info")
        self.root.after(500, lambda: self._complete_start())
    
    def _complete_start(self):
        """Complete system startup."""
        self.log("All nodes initialized", "success")
        self.log("Edge nodes: edge-1, edge-2, edge-3 (User-facing services)", "info")
        self.log("Core nodes: core-1, core-2 (Transaction coordination)", "info")
        self.log("Cloud nodes: cloud-1, cloud-2 (Persistent storage)", "info")
        self.log("System ready", "success")
        self._draw_topology()
    
    def stop_system(self):
        """Stop the distributed system."""
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_section("SYSTEM SHUTDOWN")
        self.log("System stopped", "info")
    
    def clear_logs(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)
        self.log("Logs cleared", "info")
    
    def log_section(self, section: str):
        """Add a log section header."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"\n{'='*60}\n", "log_section")
        self.log_text.insert(tk.END, f"[{timestamp}] === {section} ===\n", "log_section")
        self.log_text.insert(tk.END, f"{'='*60}\n\n", "log_section")
        self.log_text.see(tk.END)
    
    def log(self, message: str, level: str = "info"):
        """Add a log entry with better formatting."""
        timestamp = time.strftime("%H:%M:%S")
        tag = f"log_{level}"
        
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
    
    def execute_transaction(self):
        """Execute a transaction using 2PC protocol."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        transaction_id = f"TXN-{int(time.time())}"
        self.log_section("TRANSACTION EXECUTION (2PC Protocol)")
        self.log(f"Starting transaction: {transaction_id}", "info")
        self.log("Phase 1 (Voting): Coordinator sends PREPARE to participants", "info")
        self.root.after(int(self.delay_medium * 1000), lambda: self._txn_phase1_complete(transaction_id))
    
    def _txn_phase1_complete(self, txn_id: str):
        """Complete Phase 1 of transaction."""
        self.log("Phase 1: All participants voted COMMIT", "success")
        self.log("Phase 2 (Decision): Coordinator sends COMMIT to participants", "info")
        self.root.after(int(self.delay_medium * 1000), lambda: self._txn_phase2_complete(txn_id))
    
    def _txn_phase2_complete(self, txn_id: str):
        """Complete Phase 2 of transaction."""
        self.log("Phase 2: All participants acknowledged COMMIT", "success")
        self.log(f"Transaction {txn_id} COMMITTED successfully (ACID: Atomicity ensured)", "success")
        self.transactions.append({"id": txn_id, "status": "COMMITTED", "timestamp": time.time()})
    
    def abort_transaction(self):
        """Abort a transaction."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        transaction_id = f"TXN-{int(time.time())}"
        self.log_section("TRANSACTION ABORT")
        self.log(f"Starting transaction: {transaction_id}", "warning")
        self.log("Phase 1 (Voting): Coordinator sends PREPARE to participants", "info")
        self.root.after(int(self.delay_medium * 1000), lambda: self._txn_abort_phase1(transaction_id))
    
    def _txn_abort_phase1(self, txn_id: str):
        """Phase 1 abort."""
        self.log("Phase 1: Participant edge-2 voted ABORT", "error")
        self.log("Phase 2 (Decision): Coordinator sends ABORT to all participants", "info")
        self.root.after(int(self.delay_medium * 1000), lambda: self._txn_abort_complete(txn_id))
    
    def _txn_abort_complete(self, txn_id: str):
        """Complete transaction abort."""
        self.log("Phase 2: All participants acknowledged ABORT", "warning")
        self.log(f"Transaction {txn_id} ABORTED (ACID: All changes rolled back)", "error")
    
    def demonstrate_rpc(self):
        """Demonstrate RPC communication."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        self.log_section("RPC COMMUNICATION DEMONSTRATION")
        self.log("Client -> edge-1: RPC call 'get_data' with key='user:123'", "info")
        self.root.after(int(self.delay_short * 1000), lambda: self._rpc_response())
    
    def _rpc_response(self):
        """RPC response."""
        self.log("edge-1 -> Client: RPC response with data={'name': 'John', 'id': 123}", "success")
        self.log("RPC communication: Synchronous request-response completed", "success")
    
    def demonstrate_messaging(self):
        """Demonstrate client-server messaging."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        self.log_section("CLIENT-SERVER MESSAGING DEMONSTRATION")
        self.log("Client -> core-1: Message (type: REQUEST, payload: 'update_user')", "info")
        self.root.after(int(self.delay_short * 1000), lambda: self._messaging_ack())
    
    def _messaging_ack(self):
        """Messaging acknowledgment."""
        self.log("core-1 -> Client: Message (type: RESPONSE, status: ACK)", "success")
        self.log("Messaging: Guaranteed delivery with acknowledgment", "success")
    
    def demonstrate_dsm(self):
        """Demonstrate Distributed Shared Memory."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        self.log_section("DISTRIBUTED SHARED MEMORY (DSM) DEMONSTRATION")
        self.log("edge-1: DSM SET key='session:abc' value={'user': 123, 'expires': 3600}", "info")
        self.root.after(int(self.delay_short * 1000), lambda: self._dsm_replicate())
    
    def _dsm_replicate(self):
        """DSM replication."""
        self.log("DSM: Replicating to edge-2, edge-3 (consistency: weak)", "info")
        self.root.after(int(self.delay_short * 1000), lambda: self._dsm_complete())
    
    def _dsm_complete(self):
        """DSM complete."""
        self.log("edge-2: DSM GET key='session:abc' -> value={'user': 123, 'expires': 3600}", "success")
        self.log("DSM: Shared memory accessed across nodes", "success")
    
    def demonstrate_event_ordering(self):
        """Demonstrate event ordering with vector clocks."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        self.log_section("EVENT ORDERING (Vector Clocks) DEMONSTRATION")
        self.log("edge-1: Event E1, Vector Clock: {edge-1: 1, edge-2: 0, edge-3: 0}", "info")
        self.root.after(int(self.delay_short * 1000), lambda: self._event_ordering_2())
    
    def _event_ordering_2(self):
        """Event ordering step 2."""
        self.log("edge-2: Event E2, Vector Clock: {edge-1: 1, edge-2: 1, edge-3: 0}", "info")
        self.log("Event Ordering: E1 happened-before E2 (causal ordering)", "success")
        self.root.after(int(self.delay_short * 1000), lambda: self._event_ordering_complete())
    
    def _event_ordering_complete(self):
        """Event ordering complete."""
        self.log("core-1: Total order established via coordinator", "success")
    
    def demonstrate_replication(self):
        """Demonstrate data replication."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        self.log_section("REPLICATION DEMONSTRATION")
        self.log("cloud-1 (Primary): Write data key='user:456' value='data123'", "info")
        self.root.after(int(self.delay_medium * 1000), lambda: self._replication_step2())
    
    def _replication_step2(self):
        """Replication step 2."""
        self.log("Replication: cloud-1 -> cloud-2 (Replica 1)", "info")
        self.log("Replication: cloud-1 -> cloud-2 (Replica 2) - 3-way replication", "info")
        self.root.after(int(self.delay_medium * 1000), lambda: self._replication_complete())
    
    def _replication_complete(self):
        """Replication complete."""
        self.log("Replication: All replicas synchronized (active-passive replication)", "success")
        self.log("Fault Tolerance: Data available even if primary fails", "success")
    
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
        node_id = node["node_id"]
        
        self.log_section("FAULT TOLERANCE DEMONSTRATION")
        self.log(f"Monitoring: Node {node_id} heartbeat timeout (3 seconds)", "warning")
        self.root.after(int(self.delay_long * 1000), lambda: self._fault_detected(node_id))
    
    def _fault_detected(self, node_id: str):
        """Fault detected."""
        self.log(f"Failure Detection: Node {node_id} FAILED", "error")
        self.node_states[node_id] = False
        self._draw_topology()
        self.root.after(int(self.delay_medium * 1000), lambda: self._failover_start(node_id))
    
    def _failover_start(self, failed_node_id: str):
        """Start failover."""
        # Select replacement
        all_nodes = (
            self.sample_config["edge_nodes"] +
            self.sample_config["core_nodes"] +
            self.sample_config["cloud_nodes"]
        )
        replacement = None
        for node in all_nodes:
            if node["node_id"] != failed_node_id and self.node_states.get(node["node_id"], True):
                replacement = node["node_id"]
                break
        
        if replacement:
            self.log(f"Failover: Replacement node selected: {replacement}", "info")
            self.root.after(int(self.delay_medium * 1000), lambda: self._failover_complete(failed_node_id, replacement))
        else:
            self.log("Failover: No replacement available", "error")
    
    def _failover_complete(self, failed_node_id: str, replacement: str):
        """Complete failover."""
        self.log(f"Failover: Traffic redirected from {failed_node_id} to {replacement}", "info")
        self.log(f"Failover: System recovered (RTO: < 5 seconds)", "success")
    
    def recover_all_nodes(self):
        """Recover all failed nodes."""
        recovered = []
        for node_id in self.node_states:
            if not self.node_states[node_id]:
                self.node_states[node_id] = True
                recovered.append(node_id)
        
        if recovered:
            self.log_section("NODE RECOVERY")
            self.log(f"Recovery: Nodes recovered: {', '.join(recovered)}", "success")
            self._draw_topology()
        else:
            self.log("All nodes are already up", "info")
    
    def demonstrate_load_balancing(self):
        """Demonstrate load balancing."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        self.log_section("LOAD BALANCING DEMONSTRATION")
        self.log("Load Monitor: Checking node metrics (CPU, Memory, Connections)", "info")
        self.root.after(int(self.delay_short * 1000), lambda: self._load_balancing_step2())
    
    def _load_balancing_step2(self):
        """Load balancing step 2."""
        self.log("Load Metrics: edge-1 (CPU: 45%, Mem: 60%, Load: 0.52)", "info")
        self.log("Load Metrics: edge-2 (CPU: 78%, Mem: 82%, Load: 0.80) <- OVERLOADED", "warning")
        self.log("Load Metrics: edge-3 (CPU: 32%, Mem: 48%, Load: 0.40)", "info")
        self.root.after(int(self.delay_medium * 1000), lambda: self._load_balancing_complete())
    
    def _load_balancing_complete(self):
        """Load balancing complete."""
        self.log("Load Balancer: Routing new requests to edge-3 (lowest load)", "success")
        self.log("Load Balancing: Dynamic weighted round-robin applied", "success")
    
    def demonstrate_migration(self):
        """Demonstrate process migration."""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the system first")
            return
        
        self.log_section("PROCESS MIGRATION DEMONSTRATION")
        self.log("Migration Trigger: edge-2 load > 80% threshold", "warning")
        self.log("Migration: Creating checkpoint of process state on edge-2", "info")
        self.root.after(int(self.delay_medium * 1000), lambda: self._migration_step2())
    
    def _migration_step2(self):
        """Migration step 2."""
        self.log("Migration: Transferring process state from edge-2 to edge-3", "info")
        self.root.after(int(self.delay_medium * 1000), lambda: self._migration_complete())
    
    def _migration_complete(self):
        """Migration complete."""
        self.log("Migration: Process resumed on edge-3", "success")
        self.log("Migration: Load balanced across nodes", "success")
    
    def update_metrics(self):
        """Update system metrics display."""
        if self.running:
            # Count active nodes
            active_edge = sum(1 for n in self.sample_config["edge_nodes"] if self.node_states.get(n["node_id"], True))
            active_core = sum(1 for n in self.sample_config["core_nodes"] if self.node_states.get(n["node_id"], True))
            active_cloud = sum(1 for n in self.sample_config["cloud_nodes"] if self.node_states.get(n["node_id"], True))
            
            metrics = {
                "Timestamp": time.strftime("%H:%M:%S"),
                "Edge Nodes (Active/Total)": f"{active_edge}/{len(self.sample_config['edge_nodes'])}",
                "Core Nodes (Active/Total)": f"{active_core}/{len(self.sample_config['core_nodes'])}",
                "Cloud Nodes (Active/Total)": f"{active_cloud}/{len(self.sample_config['cloud_nodes'])}",
                "Active Transactions": len([t for t in self.transactions if t.get("status") == "COMMITTED"]),
                "CPU Usage": f"{random.uniform(20, 80):.1f}%",
                "Memory Usage": f"{random.uniform(30, 70):.1f}%",
                "Network Latency": f"{random.uniform(5, 50):.1f}ms",
                "Throughput": f"{random.uniform(1000, 10000):.0f} req/s"
            }
            
            self.metrics_text.delete(1.0, tk.END)
            for key, value in metrics.items():
                self.metrics_text.insert(tk.END, f"{key:25s}: {value}\n", "metrics")
        
        self.root.after(self.update_interval, self.update_metrics)


def main():
    """Main function."""
    root = tk.Tk()
    app = DistributedSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
