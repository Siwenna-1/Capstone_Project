"""Failover mechanisms for fault tolerance."""

import threading
import time
from typing import Dict, List, Optional, Callable
import logging

from ..common.logger import setup_logger

logger = setup_logger(__name__)


class NodeStatus:
    """Status of a node."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.is_active = True
        self.last_heartbeat = time.time()
        self.priority = 1  # Lower is higher priority
        self.failover_count = 0


class FailoverManager:
    """Manages failover for fault tolerance."""
    
    def __init__(self, node_id: str, heartbeat_interval: float = 1.0, timeout: float = 3.0):
        self.node_id = node_id
        self.heartbeat_interval = heartbeat_interval
        self.timeout = timeout
        self.nodes: Dict[str, NodeStatus] = {}
        self.failed_nodes: set = set()
        self.lock = threading.Lock()
        self.failover_callbacks: List[Callable] = []
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def register_node(self, node_id: str, priority: int = 1):
        """Register a node for monitoring."""
        with self.lock:
            if node_id not in self.nodes:
                self.nodes[node_id] = NodeStatus(node_id)
            self.nodes[node_id].priority = priority
            self.nodes[node_id].is_active = True
            self.nodes[node_id].last_heartbeat = time.time()
        
        logger.info(f"Registered node {node_id} for failover monitoring (priority: {priority})")
    
    def update_heartbeat(self, node_id: str):
        """Update heartbeat for a node."""
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id].last_heartbeat = time.time()
                if node_id in self.failed_nodes:
                    # Node recovered
                    self.failed_nodes.discard(node_id)
                    self.nodes[node_id].is_active = True
                    logger.info(f"Node {node_id} recovered")
    
    def start_monitoring(self):
        """Start monitoring nodes for failures."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_nodes, daemon=True)
        self.monitor_thread.start()
        logger.info("Started failover monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring nodes."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        logger.info("Stopped failover monitoring")
    
    def _monitor_nodes(self):
        """Monitor nodes for failures."""
        while self.running:
            current_time = time.time()
            failed = []
            
            with self.lock:
                for node_id, status in self.nodes.items():
                    if node_id == self.node_id:
                        continue
                    
                    if current_time - status.last_heartbeat > self.timeout:
                        if node_id not in self.failed_nodes:
                            failed.append(node_id)
                            self.failed_nodes.add(node_id)
                            status.is_active = False
            
            # Trigger failover for failed nodes
            for node_id in failed:
                logger.warning(f"Node {node_id} failed, triggering failover")
                self._trigger_failover(node_id)
            
            time.sleep(self.heartbeat_interval)
    
    def _trigger_failover(self, failed_node_id: str):
        """Trigger failover for a failed node."""
        # Find replacement node
        replacement = self._select_replacement(failed_node_id)
        
        if replacement:
            logger.info(f"Selected node {replacement} as replacement for {failed_node_id}")
            
            # Notify callbacks
            for callback in self.failover_callbacks:
                try:
                    callback(failed_node_id, replacement)
                except Exception as e:
                    logger.error(f"Error in failover callback: {e}")
        else:
            logger.error(f"No replacement available for failed node {failed_node_id}")
    
    def _select_replacement(self, failed_node_id: str) -> Optional[str]:
        """Select a replacement node."""
        with self.lock:
            if failed_node_id not in self.nodes:
                return None
            
            # Get active nodes sorted by priority
            active_nodes = [
                (node_id, status)
                for node_id, status in self.nodes.items()
                if node_id != failed_node_id and status.is_active
            ]
            
            if not active_nodes:
                return None
            
            # Sort by priority (lower is better)
            active_nodes.sort(key=lambda x: x[1].priority)
            replacement_id = active_nodes[0][0]
            
            # Update failover count
            if replacement_id in self.nodes:
                self.nodes[replacement_id].failover_count += 1
            
            return replacement_id
    
    def register_failover_callback(self, callback: Callable):
        """Register a callback for failover events."""
        self.failover_callbacks.append(callback)
    
    def get_failed_nodes(self) -> List[str]:
        """Get list of failed nodes."""
        with self.lock:
            return list(self.failed_nodes)
    
    def is_node_active(self, node_id: str) -> bool:
        """Check if a node is active."""
        with self.lock:
            if node_id in self.nodes:
                return self.nodes[node_id].is_active
            return False
