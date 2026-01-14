"""Distributed Shared Memory (DSM) implementation."""

import threading
import time
from typing import Dict, Any, Optional, Callable
from collections import defaultdict
import logging

from ..common.messages import Message, MessageType
from ..common.logger import setup_logger
from .event_ordering import VectorClock

logger = setup_logger(__name__)


class DSMEntry:
    """Entry in the distributed shared memory."""
    
    def __init__(self, key: str, value: Any, timestamp: float, node_id: str):
        self.key = key
        self.value = value
        self.timestamp = timestamp
        self.node_id = node_id
        self.version = 0
        self.lock = threading.Lock()
    
    def update(self, value: Any, timestamp: float, node_id: str):
        """Update the entry."""
        with self.lock:
            if timestamp > self.timestamp:
                self.value = value
                self.timestamp = timestamp
                self.node_id = node_id
                self.version += 1


class DistributedSharedMemory:
    """Distributed Shared Memory implementation."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.memory: Dict[str, DSMEntry] = {}
        self.lock = threading.RLock()
        self.vector_clock = VectorClock(node_id)
        self.replication_nodes: set = set()
        self.consistency_level = "weak"  # "weak", "strong", "causal"
        
        # Callbacks
        self.update_callbacks: Dict[str, Callable] = {}
    
    def set(self, key: str, value: Any):
        """Set a value in the shared memory."""
        with self.lock:
            timestamp = time.time()
            self.vector_clock.tick()
            
            if key in self.memory:
                self.memory[key].update(value, timestamp, self.node_id)
            else:
                self.memory[key] = DSMEntry(key, value, timestamp, self.node_id)
            
            # Trigger callbacks
            if key in self.update_callbacks:
                self.update_callbacks[key](key, value, self.node_id)
            
            logger.debug(f"DSM SET: {key} = {value} (node: {self.node_id})")
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the shared memory."""
        with self.lock:
            if key in self.memory:
                return self.memory[key].value
            return None
    
    def delete(self, key: str):
        """Delete a key from the shared memory."""
        with self.lock:
            if key in self.memory:
                del self.memory[key]
                logger.debug(f"DSM DELETE: {key} (node: {self.node_id})")
    
    def update_from_remote(self, key: str, value: Any, timestamp: float, node_id: str, 
                          vector_clock: Dict[str, int]):
        """Update memory from a remote node."""
        with self.lock:
            # Update vector clock
            self.vector_clock.update(vector_clock)
            
            # Apply consistency model
            if self.consistency_level == "strong":
                # Strong consistency: wait for all updates
                if key not in self.memory or timestamp > self.memory[key].timestamp:
                    self.set(key, value)
            elif self.consistency_level == "causal":
                # Causal consistency: respect causal ordering
                if self.vector_clock.happened_before(vector_clock):
                    self.set(key, value)
            else:
                # Weak consistency: last write wins
                if key not in self.memory or timestamp > self.memory[key].timestamp:
                    if key in self.memory:
                        self.memory[key].update(value, timestamp, node_id)
                    else:
                        self.memory[key] = DSMEntry(key, value, timestamp, node_id)
    
    def register_callback(self, key: str, callback: Callable):
        """Register a callback for updates to a key."""
        self.update_callbacks[key] = callback
    
    def get_all_keys(self) -> list:
        """Get all keys in the memory."""
        with self.lock:
            return list(self.memory.keys())
    
    def get_vector_clock(self) -> Dict[str, int]:
        """Get the current vector clock."""
        return self.vector_clock.get_clock()
    
    def replicate_to_nodes(self, key: str, value: Any, nodes: list):
        """Replicate a value to other nodes."""
        # This would typically use network communication
        # For now, it's a placeholder for the replication mechanism
        logger.debug(f"Replicating {key} to {len(nodes)} nodes")
        pass
