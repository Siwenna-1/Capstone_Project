"""Process migration for load optimization."""

import threading
import time
from typing import Dict, List, Optional, Any, Callable
import logging

from ..common.logger import setup_logger

logger = setup_logger(__name__)


class ProcessState:
    """State of a process."""
    
    def __init__(self, process_id: str, node_id: str):
        self.process_id = process_id
        self.node_id = node_id
        self.state: Dict[str, Any] = {}
        self.checkpoint_time: Optional[float] = None


class MigrationManager:
    """Manages process migration for load optimization."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.processes: Dict[str, ProcessState] = {}
        self.migration_threshold = 0.8  # Migrate if load > 80%
        self.lock = threading.Lock()
        self.migration_callbacks: List[Callable] = []
    
    def register_process(self, process_id: str, state: Dict[str, Any] = None):
        """Register a process for potential migration."""
        with self.lock:
            self.processes[process_id] = ProcessState(process_id, self.node_id)
            if state:
                self.processes[process_id].state = state
        
        logger.debug(f"Registered process {process_id} for migration")
    
    def checkpoint_process(self, process_id: str, state: Dict[str, Any]):
        """Create a checkpoint of a process state."""
        with self.lock:
            if process_id in self.processes:
                self.processes[process_id].state = state
                self.processes[process_id].checkpoint_time = time.time()
        
        logger.debug(f"Checkpointed process {process_id}")
    
    def migrate_process(self, process_id: str, target_node_id: str) -> bool:
        """Migrate a process to another node."""
        with self.lock:
            if process_id not in self.processes:
                logger.error(f"Process {process_id} not found")
                return False
            
            process = self.processes[process_id]
        
        logger.info(f"Migrating process {process_id} from {self.node_id} to {target_node_id}")
        
        # Create checkpoint
        checkpoint = process.state.copy()
        
        # Notify callbacks
        for callback in self.migration_callbacks:
            try:
                callback(process_id, self.node_id, target_node_id, checkpoint)
            except Exception as e:
                logger.error(f"Error in migration callback: {e}")
        
        # Update process state
        with self.lock:
            process.node_id = target_node_id
            process.checkpoint_time = time.time()
        
        logger.info(f"Process {process_id} migrated to {target_node_id}")
        return True
    
    def should_migrate(self, node_load: float) -> bool:
        """Determine if processes should be migrated based on node load."""
        return node_load > self.migration_threshold
    
    def select_process_to_migrate(self, node_load: float) -> Optional[str]:
        """Select a process to migrate."""
        if not self.should_migrate(node_load):
            return None
        
        with self.lock:
            if not self.processes:
                return None
            
            # Select process with most recent checkpoint
            processes_with_checkpoints = [
                (pid, proc) for pid, proc in self.processes.items()
                if proc.checkpoint_time is not None
            ]
            
            if not processes_with_checkpoints:
                # Select any process
                process_id = list(self.processes.keys())[0]
                return process_id
            
            # Select process with oldest checkpoint (easiest to migrate)
            process_id, _ = min(processes_with_checkpoints, key=lambda x: x[1].checkpoint_time)
            return process_id
    
    def register_migration_callback(self, callback: Callable):
        """Register a callback for migration events."""
        self.migration_callbacks.append(callback)
    
    def get_process_state(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of a process."""
        with self.lock:
            if process_id in self.processes:
                return self.processes[process_id].state.copy()
            return None
