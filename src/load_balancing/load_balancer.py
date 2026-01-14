"""Load balancer for dynamic load distribution."""

import threading
import time
from typing import Dict, List, Optional, Callable
import random
import logging

from ..common.logger import setup_logger

logger = setup_logger(__name__)


class NodeMetrics:
    """Metrics for a node."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.active_connections = 0
        self.response_latency = 0.0
        self.queue_depth = 0
        self.last_update = time.time()
        self.weight = 1.0
    
    def calculate_load_score(self) -> float:
        """Calculate load score (higher = more loaded)."""
        # Weighted combination of metrics
        cpu_weight = 0.3
        memory_weight = 0.3
        connection_weight = 0.2
        latency_weight = 0.2
        
        score = (
            cpu_weight * self.cpu_usage +
            memory_weight * self.memory_usage +
            connection_weight * min(self.active_connections / 1000.0, 1.0) +
            latency_weight * min(self.response_latency / 100.0, 1.0)
        )
        
        return score


class LoadBalancer:
    """Load balancer for distributing load across nodes."""
    
    def __init__(self, node_id: str, algorithm: str = "weighted_round_robin"):
        self.node_id = node_id
        self.algorithm = algorithm
        self.nodes: Dict[str, NodeMetrics] = {}
        self.routing_weights: Dict[str, float] = {}
        self.current_index: Dict[str, int] = {}  # For round-robin
        self.lock = threading.Lock()
        self.update_interval = 5.0  # Update weights every 5 seconds
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
    
    def register_node(self, node_id: str, initial_weight: float = 1.0):
        """Register a node for load balancing."""
        with self.lock:
            if node_id not in self.nodes:
                self.nodes[node_id] = NodeMetrics(node_id)
                self.routing_weights[node_id] = initial_weight
                self.current_index[node_id] = 0
        
        logger.info(f"Registered node {node_id} for load balancing (weight: {initial_weight})")
    
    def update_metrics(self, node_id: str, cpu: float, memory: float, 
                      connections: int, latency: float, queue_depth: int = 0):
        """Update metrics for a node."""
        with self.lock:
            if node_id in self.nodes:
                metrics = self.nodes[node_id]
                metrics.cpu_usage = cpu
                metrics.memory_usage = memory
                metrics.active_connections = connections
                metrics.response_latency = latency
                metrics.queue_depth = queue_depth
                metrics.last_update = time.time()
    
    def select_node(self, service_type: str = "default") -> Optional[str]:
        """Select a node for routing based on the load balancing algorithm."""
        with self.lock:
            active_nodes = [
                (node_id, metrics)
                for node_id, metrics in self.nodes.items()
                if metrics.last_update > time.time() - 10.0  # Only consider recently updated nodes
            ]
            
            if not active_nodes:
                return None
            
            if self.algorithm == "weighted_round_robin":
                return self._weighted_round_robin(active_nodes)
            elif self.algorithm == "least_connections":
                return self._least_connections(active_nodes)
            elif self.algorithm == "least_load":
                return self._least_load(active_nodes)
            else:
                return self._weighted_round_robin(active_nodes)
    
    def _weighted_round_robin(self, nodes: List[tuple]) -> str:
        """Weighted round-robin selection."""
        if not nodes:
            return None
        
        # Calculate total weight
        total_weight = sum(self.routing_weights.get(node_id, 1.0) for node_id, _ in nodes)
        
        if total_weight == 0:
            # Fallback to simple round-robin
            node_id, _ = nodes[self.current_index.get("default", 0) % len(nodes)]
            self.current_index["default"] = (self.current_index.get("default", 0) + 1) % len(nodes)
            return node_id
        
        # Weighted selection
        rand = random.uniform(0, total_weight)
        cumulative = 0
        
        for node_id, _ in nodes:
            weight = self.routing_weights.get(node_id, 1.0)
            cumulative += weight
            if rand <= cumulative:
                return node_id
        
        # Fallback
        return nodes[0][0]
    
    def _least_connections(self, nodes: List[tuple]) -> str:
        """Select node with least connections."""
        if not nodes:
            return None
        
        min_connections = min(metrics.active_connections for _, metrics in nodes)
        candidates = [
            node_id for node_id, metrics in nodes
            if metrics.active_connections == min_connections
        ]
        
        return random.choice(candidates) if candidates else nodes[0][0]
    
    def _least_load(self, nodes: List[tuple]) -> str:
        """Select node with least load score."""
        if not nodes:
            return None
        
        min_load = min(metrics.calculate_load_score() for _, metrics in nodes)
        candidates = [
            node_id for node_id, metrics in nodes
            if metrics.calculate_load_score() == min_load
        ]
        
        return random.choice(candidates) if candidates else nodes[0][0]
    
    def start_updates(self):
        """Start periodic weight updates."""
        if self.running:
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_weights, daemon=True)
        self.update_thread.start()
        logger.info("Started load balancer weight updates")
    
    def stop_updates(self):
        """Stop periodic weight updates."""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
        logger.info("Stopped load balancer weight updates")
    
    def _update_weights(self):
        """Update routing weights based on node metrics."""
        while self.running:
            with self.lock:
                for node_id, metrics in self.nodes.items():
                    # Calculate weight based on load (inverse relationship)
                    load_score = metrics.calculate_load_score()
                    
                    # Weight = 1 / (load + 0.1) to avoid division by zero
                    # Higher load = lower weight
                    new_weight = 1.0 / (load_score + 0.1)
                    
                    # Normalize weight (0.1 to 10.0)
                    new_weight = max(0.1, min(10.0, new_weight))
                    
                    self.routing_weights[node_id] = new_weight
            
            time.sleep(self.update_interval)
    
    def get_node_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all nodes."""
        with self.lock:
            stats = {}
            for node_id, metrics in self.nodes.items():
                stats[node_id] = {
                    "cpu": metrics.cpu_usage,
                    "memory": metrics.memory_usage,
                    "connections": metrics.active_connections,
                    "latency": metrics.response_latency,
                    "load_score": metrics.calculate_load_score(),
                    "weight": self.routing_weights.get(node_id, 1.0)
                }
            return stats
