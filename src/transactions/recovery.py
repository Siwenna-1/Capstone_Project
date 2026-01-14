"""Transaction recovery mechanisms."""

import threading
import time
from typing import Dict, List, Optional
import logging

from ..common.logger import setup_logger
from .two_phase_commit import TransactionState

logger = setup_logger(__name__)


class TransactionLog:
    """Transaction log for recovery."""
    
    def __init__(self):
        self.log: List[Dict] = []
        self.lock = threading.Lock()
    
    def append(self, entry: Dict):
        """Append an entry to the log."""
        with self.lock:
            entry["timestamp"] = time.time()
            self.log.append(entry)
            # In a real implementation, write to disk
    
    def get_transaction_entries(self, transaction_id: str) -> List[Dict]:
        """Get all entries for a transaction."""
        with self.lock:
            return [entry for entry in self.log if entry.get("transaction_id") == transaction_id]
    
    def get_uncommitted_transactions(self) -> List[str]:
        """Get list of uncommitted transactions."""
        with self.lock:
            transaction_ids = set()
            for entry in self.log:
                txn_id = entry.get("transaction_id")
                if txn_id and entry.get("status") not in ["COMMITTED", "ABORTED"]:
                    transaction_ids.add(txn_id)
            return list(transaction_ids)


class RecoveryManager:
    """Manages transaction recovery."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.transaction_log = TransactionLog()
        self.lock = threading.Lock()
    
    def log_transaction_start(self, transaction_id: str, participants: List[str]):
        """Log the start of a transaction."""
        self.transaction_log.append({
            "type": "START",
            "transaction_id": transaction_id,
            "participants": participants,
            "node_id": self.node_id
        })
    
    def log_prepare(self, transaction_id: str):
        """Log PREPARE phase."""
        self.transaction_log.append({
            "type": "PREPARE",
            "transaction_id": transaction_id,
            "node_id": self.node_id
        })
    
    def log_commit(self, transaction_id: str):
        """Log COMMIT."""
        self.transaction_log.append({
            "type": "COMMIT",
            "transaction_id": transaction_id,
            "status": "COMMITTED",
            "node_id": self.node_id
        })
    
    def log_abort(self, transaction_id: str):
        """Log ABORT."""
        self.transaction_log.append({
            "type": "ABORT",
            "transaction_id": transaction_id,
            "status": "ABORTED",
            "node_id": self.node_id
        })
    
    def recover(self) -> List[str]:
        """Recover from failures."""
        uncommitted = self.transaction_log.get_uncommitted_transactions()
        logger.info(f"Recovery: Found {len(uncommitted)} uncommitted transactions")
        
        for txn_id in uncommitted:
            entries = self.transaction_log.get_transaction_entries(txn_id)
            # Determine state and recover
            # In a real implementation, this would coordinate with other nodes
            logger.info(f"Recovery: Transaction {txn_id} needs recovery")
        
        return uncommitted
