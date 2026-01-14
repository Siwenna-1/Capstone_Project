"""Core node implementation for coordination."""

import threading
import time
import json
import argparse
from typing import Dict, Any, Optional, List
import logging

from ..common.logger import setup_logger
from ..common.messages import MessageType
from ..communication.rpc import RPCServer
from ..communication.messaging import MessagingServer
from ..communication.event_ordering import EventOrderer
from ..transactions.transaction_manager import TransactionManager
from ..fault_tolerance.failover import FailoverManager
from ..load_balancing.load_balancer import LoadBalancer

logger = setup_logger(__name__)


class CoreNode:
    """Core node for coordination and transaction management."""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 8002)
        self.rpc_port = config.get("rpc_port", 9002)
        
        # Components
        self.rpc_server: Optional[RPCServer] = None
        self.messaging_server: Optional[MessagingServer] = None
        self.event_orderer = EventOrderer(node_id)
        self.transaction_manager = TransactionManager(node_id)
        self.failover_manager = FailoverManager(node_id)
        self.load_balancer = LoadBalancer(node_id)
        
        # State
        self.edge_nodes: list = config.get("edge_nodes", [])
        self.cloud_nodes: list = config.get("cloud_nodes", [])
        self.is_running = False
        
        # Metrics
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "active_transactions": 0,
            "transactions_committed": 0,
            "transactions_aborted": 0
        }
    
    def start(self):
        """Start the core node."""
        logger.info(f"Starting core node {self.node_id}")
        
        # Start RPC server
        self.rpc_server = RPCServer(self.host, self.rpc_port, self.node_id)
        self.rpc_server.register_handler("begin_transaction", self.handle_begin_transaction)
        self.rpc_server.register_handler("execute_transaction", self.handle_execute_transaction)
        self.rpc_server.register_handler("get_metrics", self.handle_get_metrics)
        self.rpc_server.start()
        
        # Start messaging server
        self.messaging_server = MessagingServer(self.host, self.port, self.node_id)
        self.messaging_server.start()
        
        # Start failover monitoring
        self.failover_manager.start_monitoring()
        
        # Start load balancer
        self.load_balancer.start_updates()
        
        self.is_running = True
        logger.info(f"Core node {self.node_id} started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the core node."""
        logger.info(f"Stopping core node {self.node_id}")
        self.is_running = False
        
        if self.rpc_server:
            self.rpc_server.stop()
        if self.messaging_server:
            self.messaging_server.stop()
        if self.failover_manager:
            self.failover_manager.stop_monitoring()
        if self.load_balancer:
            self.load_balancer.stop_updates()
        
        logger.info(f"Core node {self.node_id} stopped")
    
    def handle_begin_transaction(self, participants: List[str]) -> str:
        """Handle begin transaction request."""
        transaction_id = self.transaction_manager.begin_transaction(participants)
        self.metrics["active_transactions"] += 1
        return transaction_id
    
    def handle_execute_transaction(self, transaction_id: str, operations: List[Dict[str, Any]]) -> bool:
        """Handle execute transaction request."""
        success = self.transaction_manager.execute_transaction(transaction_id, operations)
        
        if success:
            self.metrics["transactions_committed"] += 1
        else:
            self.metrics["transactions_aborted"] += 1
        
        self.metrics["active_transactions"] = max(0, self.metrics["active_transactions"] - 1)
        return success
    
    def handle_get_metrics(self) -> Dict[str, Any]:
        """Handle get metrics request."""
        return self.metrics


def main():
    """Main function for core node."""
    parser = argparse.ArgumentParser(description="Core Node")
    parser.add_argument("--config", type=str, default="config/core_config.json",
                       help="Configuration file path")
    parser.add_argument("--node-id", type=str, default="core-1",
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
    node = CoreNode(args.node_id, config)
    
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
