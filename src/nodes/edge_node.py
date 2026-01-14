"""Edge node implementation."""

import threading
import time
import json
import argparse
from typing import Dict, Any, Optional
import logging

from ..common.logger import setup_logger
from ..common.messages import MessageType
from ..communication.rpc import RPCServer, RPCClient
from ..communication.messaging import MessagingServer, MessagingClient
from ..communication.dsm import DistributedSharedMemory
from ..fault_tolerance.failover import FailoverManager
from ..load_balancing.load_balancer import LoadBalancer

logger = setup_logger(__name__)


class EdgeNode:
    """Edge node for low-latency service delivery."""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 8001)
        self.rpc_port = config.get("rpc_port", 9001)
        
        # Components
        self.rpc_server: Optional[RPCServer] = None
        self.rpc_client: Optional[RPCClient] = None
        self.messaging_server: Optional[MessagingServer] = None
        self.dsm = DistributedSharedMemory(node_id)
        self.failover_manager = FailoverManager(node_id)
        self.load_balancer = LoadBalancer(node_id)
        
        # State
        self.cache: Dict[str, Any] = {}
        self.core_nodes: list = config.get("core_nodes", [])
        self.cloud_nodes: list = config.get("cloud_nodes", [])
        self.is_running = False
        
        # Metrics
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "active_connections": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def start(self):
        """Start the edge node."""
        logger.info(f"Starting edge node {self.node_id}")
        
        # Start RPC server
        self.rpc_server = RPCServer(self.host, self.rpc_port, self.node_id)
        self.rpc_server.register_handler("get_data", self.handle_get_data)
        self.rpc_server.register_handler("set_data", self.handle_set_data)
        self.rpc_server.register_handler("get_metrics", self.handle_get_metrics)
        self.rpc_server.start()
        
        # Start messaging server
        self.messaging_server = MessagingServer(self.host, self.port, self.node_id)
        self.messaging_server.register_handler(self.messaging_server.message_handlers.get(MessageType.REQUEST, None))
        self.messaging_server.start()
        
        # Start failover monitoring
        self.failover_manager.start_monitoring()
        
        # Start load balancer
        self.load_balancer.start_updates()
        
        self.is_running = True
        logger.info(f"Edge node {self.node_id} started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the edge node."""
        logger.info(f"Stopping edge node {self.node_id}")
        self.is_running = False
        
        if self.rpc_server:
            self.rpc_server.stop()
        if self.messaging_server:
            self.messaging_server.stop()
        if self.failover_manager:
            self.failover_manager.stop_monitoring()
        if self.load_balancer:
            self.load_balancer.stop_updates()
        
        logger.info(f"Edge node {self.node_id} stopped")
    
    def handle_get_data(self, key: str) -> Optional[Any]:
        """Handle get data request."""
        # Check cache first
        if key in self.cache:
            self.metrics["cache_hits"] += 1
            return self.cache[key]
        
        # Cache miss - would query core/cloud nodes
        self.metrics["cache_misses"] += 1
        return None
    
    def handle_set_data(self, key: str, value: Any) -> bool:
        """Handle set data request."""
        self.cache[key] = value
        # Update DSM
        self.dsm.set(key, value)
        return True
    
    def handle_get_metrics(self) -> Dict[str, Any]:
        """Handle get metrics request."""
        return self.metrics
    
    def update_metrics(self, cpu: float, memory: float, connections: int):
        """Update node metrics."""
        self.metrics["cpu_usage"] = cpu
        self.metrics["memory_usage"] = memory
        self.metrics["active_connections"] = connections


def main():
    """Main function for edge node."""
    parser = argparse.ArgumentParser(description="Edge Node")
    parser.add_argument("--config", type=str, default="config/edge_config.json",
                       help="Configuration file path")
    parser.add_argument("--node-id", type=str, default="edge-1",
                       help="Node ID")
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
        logger.warning(f"Config file {args.config} not found, using defaults")
    
    # Create and start node
    node = EdgeNode(args.node_id, config)
    
    try:
        node.start()
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        node.stop()


if __name__ == "__main__":
    main()
