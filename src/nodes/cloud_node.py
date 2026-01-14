"""Cloud node implementation for storage."""

import threading
import time
import json
import argparse
from typing import Dict, Any, Optional
import logging

from ..common.logger import setup_logger
from ..common.messages import MessageType
from ..communication.rpc import RPCServer
from ..communication.messaging import MessagingServer
from ..fault_tolerance.replication import ReplicationManager, ReplicationStrategy
from ..fault_tolerance.failover import FailoverManager

logger = setup_logger(__name__)


class CloudNode:
    """Cloud node for persistent storage."""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 8003)
        self.rpc_port = config.get("rpc_port", 9003)
        
        # Components
        self.rpc_server: Optional[RPCServer] = None
        self.messaging_server: Optional[MessagingServer] = None
        self.replication_manager = ReplicationManager(node_id, ReplicationStrategy.ACTIVE_PASSIVE)
        self.failover_manager = FailoverManager(node_id)
        
        # State
        self.storage: Dict[str, Any] = {}
        self.transaction_log: list = []
        self.core_nodes: list = config.get("core_nodes", [])
        self.is_running = False
        
        # Metrics
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "storage_size": 0,
            "writes": 0,
            "reads": 0
        }
    
    def start(self):
        """Start the cloud node."""
        logger.info(f"Starting cloud node {self.node_id}")
        
        # Start RPC server
        self.rpc_server = RPCServer(self.host, self.rpc_port, self.node_id)
        self.rpc_server.register_handler("read", self.handle_read)
        self.rpc_server.register_handler("write", self.handle_write)
        self.rpc_server.register_handler("get_metrics", self.handle_get_metrics)
        self.rpc_server.start()
        
        # Start messaging server
        self.messaging_server = MessagingServer(self.host, self.port, self.node_id)
        self.messaging_server.start()
        
        # Start failover monitoring
        self.failover_manager.start_monitoring()
        
        self.is_running = True
        logger.info(f"Cloud node {self.node_id} started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the cloud node."""
        logger.info(f"Stopping cloud node {self.node_id}")
        self.is_running = False
        
        if self.rpc_server:
            self.rpc_server.stop()
        if self.messaging_server:
            self.messaging_server.stop()
        if self.failover_manager:
            self.failover_manager.stop_monitoring()
        
        logger.info(f"Cloud node {self.node_id} stopped")
    
    def handle_read(self, key: str) -> Optional[Any]:
        """Handle read request."""
        self.metrics["reads"] += 1
        return self.storage.get(key)
    
    def handle_write(self, key: str, value: Any) -> bool:
        """Handle write request."""
        self.storage[key] = value
        self.metrics["writes"] += 1
        self.metrics["storage_size"] = len(self.storage)
        
        # Log transaction
        self.transaction_log.append({
            "timestamp": time.time(),
            "operation": "write",
            "key": key,
            "value": value
        })
        
        return True
    
    def handle_get_metrics(self) -> Dict[str, Any]:
        """Handle get metrics request."""
        return self.metrics


def main():
    """Main function for cloud node."""
    parser = argparse.ArgumentParser(description="Cloud Node")
    parser.add_argument("--config", type=str, default="config/cloud_config.json",
                       help="Configuration file path")
    parser.add_argument("--node-id", type=str, default="cloud-1",
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
    node = CloudNode(args.node_id, config)
    
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
