"""Transaction manager for distributed transactions."""

import threading
import time
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import logging

from ..common.utils import generate_transaction_id
from ..common.logger import setup_logger
from .two_phase_commit import TwoPhaseCommit, TransactionState

logger = setup_logger(__name__)


class Transaction:
    """Represents a distributed transaction."""
    
    def __init__(self, transaction_id: str, coordinator_id: str):
        self.transaction_id = transaction_id
        self.coordinator_id = coordinator_id
        self.participants: List[str] = []
        self.operations: List[Dict[str, Any]] = []
        self.state = TransactionState.INITIAL
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.lock = threading.Lock()
    
    def add_participant(self, participant_id: str):
        """Add a participant to the transaction."""
        with self.lock:
            if participant_id not in self.participants:
                self.participants.append(participant_id)
    
    def add_operation(self, operation: Dict[str, Any]):
        """Add an operation to the transaction."""
        with self.lock:
            self.operations.append(operation)
    
    def set_state(self, state: TransactionState):
        """Set the transaction state."""
        with self.lock:
            self.state = state
            if state in [TransactionState.COMMITTED, TransactionState.ABORTED]:
                self.end_time = time.time()


class TransactionManager:
    """Manages distributed transactions."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.transactions: Dict[str, Transaction] = {}
        self.active_transactions: set = set()
        self.two_phase_commit = TwoPhaseCommit(node_id)
        self.transaction_log: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def begin_transaction(self, participants: List[str]) -> str:
        """Begin a new transaction."""
        transaction_id = generate_transaction_id()
        
        with self.lock:
            transaction = Transaction(transaction_id, self.node_id)
            for participant in participants:
                transaction.add_participant(participant)
            self.transactions[transaction_id] = transaction
            self.active_transactions.add(transaction_id)
        
        logger.info(f"Transaction {transaction_id} started with {len(participants)} participants")
        return transaction_id
    
    def execute_transaction(self, transaction_id: str, operations: List[Dict[str, Any]]) -> bool:
        """Execute a transaction using 2PC."""
        with self.lock:
            if transaction_id not in self.transactions:
                logger.error(f"Transaction {transaction_id} not found")
                return False
            
            transaction = self.transactions[transaction_id]
            for op in operations:
                transaction.add_operation(op)
        
        # Execute using 2PC
        success = self.two_phase_commit.execute(transaction_id, transaction.participants, operations)
        
        with self.lock:
            if success:
                transaction.set_state(TransactionState.COMMITTED)
                self.active_transactions.discard(transaction_id)
                self._log_transaction(transaction, "COMMITTED")
            else:
                transaction.set_state(TransactionState.ABORTED)
                self.active_transactions.discard(transaction_id)
                self._log_transaction(transaction, "ABORTED")
        
        return success
    
    def abort_transaction(self, transaction_id: str):
        """Abort a transaction."""
        with self.lock:
            if transaction_id not in self.transactions:
                return
            
            transaction = self.transactions[transaction_id]
            transaction.set_state(TransactionState.ABORTED)
            self.active_transactions.discard(transaction_id)
            self._log_transaction(transaction, "ABORTED")
        
        logger.info(f"Transaction {transaction_id} aborted")
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID."""
        with self.lock:
            return self.transactions.get(transaction_id)
    
    def get_active_transactions(self) -> List[str]:
        """Get list of active transaction IDs."""
        with self.lock:
            return list(self.active_transactions)
    
    def _log_transaction(self, transaction: Transaction, status: str):
        """Log a transaction."""
        log_entry = {
            "transaction_id": transaction.transaction_id,
            "coordinator": transaction.coordinator_id,
            "participants": transaction.participants,
            "operations": transaction.operations,
            "status": status,
            "start_time": transaction.start_time,
            "end_time": transaction.end_time,
            "duration": transaction.end_time - transaction.start_time if transaction.end_time else None
        }
        self.transaction_log.append(log_entry)
        
        # Keep only last 1000 transactions in memory
        if len(self.transaction_log) > 1000:
            self.transaction_log = self.transaction_log[-1000:]
