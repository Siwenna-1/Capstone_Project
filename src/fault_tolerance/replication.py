"""Replication mechanisms for fault tolerance."""

import threading
import time
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import logging

from ..common.logger import setup_logger

logger = setup_logger(__name__)


class ReplicationStrategy(Enum):
    """Replication strategies."""
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"
    QUORUM = "quorum"


class Replica:
    """Represents a replica."""
    
    def __init__(self, replica_id: str, node_id: str, is_primary: bool = False):
        self.replica_id = replica_id
        self.node_id = node_id
        self.is_primary = is_primary
        self.is_active = True
        self.last_heartbeat = time.time()
        self.state: Dict[str, Any] = {}


class ReplicationManager:
    """Manages replication for fault tolerance."""
    
    def __init__(self, node_id: str, strategy: ReplicationStrategy = ReplicationStrategy.ACTIVE_PASSIVE):
        self.node_id = node_id
        self.strategy = strategy
        self.replicas: Dict[str, List[Replica]] = {}  # {key: [replicas]}
        self.primary_replicas: Dict[str, str] = {}  # {key: primary_node_id}
        self.lock = threading.Lock()
        self.replication_callbacks: Dict[str, Callable] = {}
    
    def add_replica(self, key: str, replica_id: str, node_id: str, is_primary: bool = False):
        """Add a replica for a key."""
        with self.lock:
            if key not in self.replicas:
                self.replicas[key] = []
            
            replica = Replica(replica_id, node_id, is_primary)
            self.replicas[key].append(replica)
            
            if is_primary:
                self.primary_replicas[key] = node_id
        
        logger.info(f"Added replica {replica_id} for key {key} (primary: {is_primary})")
    
    def replicate(self, key: str, value: Any, node_id: str) -> bool:
        """Replicate a value to all replicas."""
        with self.lock:
            if key not in self.replicas:
                return False
            
            replicas = self.replicas[key]
            success_count = 0
            
            for replica in replicas:
                if replica.node_id != node_id and replica.is_active:
                    # In a real implementation, this would send the value to the replica
                    if key in self.replication_callbacks:
                        try:
                            self.replication_callbacks[key](replica.node_id, key, value)
                            success_count += 1
                        except Exception as e:
                            logger.error(f"Error replicating to {replica.node_id}: {e}")
            
            logger.debug(f"Replicated {key} to {success_count}/{len(replicas)-1} replicas")
            return success_count > 0
    
    def get_primary(self, key: str) -> Optional[str]:
        """Get the primary replica for a key."""
        with self.lock:
            return self.primary_replicas.get(key)
    
    def promote_replica(self, key: str, replica_node_id: str):
        """Promote a replica to primary (failover)."""
        with self.lock:
            if key not in self.replicas:
                return
            
            for replica in self.replicas[key]:
                if replica.node_id == replica_node_id:
                    replica.is_primary = True
                    self.primary_replicas[key] = replica_node_id
                else:
                    replica.is_primary = False
            
            logger.info(f"Promoted replica {replica_node_id} to primary for key {key}")
    
    def update_heartbeat(self, replica_id: str):
        """Update heartbeat for a replica."""
        with self.lock:
            for replicas in self.replicas.values():
                for replica in replicas:
                    if replica.replica_id == replica_id:
                        replica.last_heartbeat = time.time()
                        break
    
    def check_health(self, timeout: float = 3.0) -> Dict[str, List[str]]:
        """Check health of replicas and return failed ones."""
        current_time = time.time()
        failed: Dict[str, List[str]] = {}
        
        with self.lock:
            for key, replicas in self.replicas.items():
                failed_replicas = []
                for replica in replicas:
                    if current_time - replica.last_heartbeat > timeout:
                        replica.is_active = False
                        failed_replicas.append(replica.node_id)
                    else:
                        replica.is_active = True
                
                if failed_replicas:
                    failed[key] = failed_replicas
        
        return failed
    
    def register_replication_callback(self, key: str, callback: Callable):
        """Register a callback for replication."""
        self.replication_callbacks[key] = callback
