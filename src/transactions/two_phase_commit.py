"""Two-Phase Commit (2PC) protocol implementation."""

import threading
import time
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import logging

from ..common.logger import setup_logger
from ..common.messages import Message, MessageType

logger = setup_logger(__name__)


class TransactionState(Enum):
    """Transaction states in 2PC."""
    INITIAL = "initial"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"
    WAIT = "wait"  # Waiting for coordinator decision


class TwoPhaseCommit:
    """Two-Phase Commit protocol implementation."""
    
    def __init__(self, node_id: str, timeout: float = 30.0):
        self.node_id = node_id
        self.timeout = timeout
        self.transactions: Dict[str, Dict[str, Any]] = {}
        self.votes: Dict[str, Dict[str, str]] = {}  # {txn_id: {participant: vote}}
        self.lock = threading.Lock()
        
        # Callback for sending messages to participants
        self.send_message_callback: Optional[Callable] = None
    
    def set_send_callback(self, callback: Callable):
        """Set callback for sending messages."""
        self.send_message_callback = callback
    
    def execute(self, transaction_id: str, participants: List[str], 
                operations: List[Dict[str, Any]]) -> bool:
        """Execute a transaction using 2PC protocol."""
        with self.lock:
            self.transactions[transaction_id] = {
                "participants": participants,
                "operations": operations,
                "state": TransactionState.INITIAL,
                "start_time": time.time()
            }
            self.votes[transaction_id] = {}
        
        # Phase 1: Voting
        logger.info(f"Transaction {transaction_id}: Starting Phase 1 (Voting)")
        all_voted = self._phase1_voting(transaction_id, participants, operations)
        
        if not all_voted:
            self._abort_transaction(transaction_id)
            return False
        
        # Check votes
        commit_votes = sum(1 for vote in self.votes[transaction_id].values() if vote == "COMMIT")
        
        if commit_votes == len(participants):
            # Phase 2: Commit
            logger.info(f"Transaction {transaction_id}: All votes COMMIT, starting Phase 2 (Commit)")
            success = self._phase2_commit(transaction_id, participants)
            return success
        else:
            # Phase 2: Abort
            logger.info(f"Transaction {transaction_id}: Some votes ABORT, aborting transaction")
            self._abort_transaction(transaction_id)
            return False
    
    def _phase1_voting(self, transaction_id: str, participants: List[str], 
                      operations: List[Dict[str, Any]]) -> bool:
        """Phase 1: Send PREPARE messages and collect votes."""
        with self.lock:
            self.transactions[transaction_id]["state"] = TransactionState.PREPARING
        
        # Send PREPARE messages to all participants
        prepare_messages = []
        for participant in participants:
            if self.send_message_callback:
                message = Message.create_request(
                    sender_id=self.node_id,
                    receiver_id=participant,
                    payload={
                        "type": "PREPARE",
                        "transaction_id": transaction_id,
                        "operations": operations
                    }
                )
                prepare_messages.append((participant, message))
                if self.send_message_callback:
                    self.send_message_callback(message)
        
        # Wait for votes (simplified - in real implementation, use async/await)
        time.sleep(0.1)  # Simulate network delay
        
        # In a real implementation, votes would come via message handlers
        # For now, we simulate that all participants vote COMMIT
        with self.lock:
            for participant in participants:
                if participant not in self.votes[transaction_id]:
                    self.votes[transaction_id][participant] = "COMMIT"  # Simulated
        
        return True
    
    def _phase2_commit(self, transaction_id: str, participants: List[str]) -> bool:
        """Phase 2: Send COMMIT messages."""
        with self.lock:
            self.transactions[transaction_id]["state"] = TransactionState.COMMITTING
        
        # Send COMMIT messages to all participants
        for participant in participants:
            if self.send_message_callback:
                message = Message.create_request(
                    sender_id=self.node_id,
                    receiver_id=participant,
                    payload={
                        "type": "COMMIT",
                        "transaction_id": transaction_id
                    }
                )
                self.send_message_callback(message)
        
        # Wait for acknowledgments
        time.sleep(0.1)  # Simulate network delay
        
        with self.lock:
            self.transactions[transaction_id]["state"] = TransactionState.COMMITTED
            self.transactions[transaction_id]["end_time"] = time.time()
        
        logger.info(f"Transaction {transaction_id}: Committed successfully")
        return True
    
    def _abort_transaction(self, transaction_id: str):
        """Abort a transaction."""
        with self.lock:
            self.transactions[transaction_id]["state"] = TransactionState.ABORTING
        
        participants = self.transactions[transaction_id]["participants"]
        
        # Send ABORT messages to all participants
        for participant in participants:
            if self.send_message_callback:
                message = Message.create_request(
                    sender_id=self.node_id,
                    receiver_id=participant,
                    payload={
                        "type": "ABORT",
                        "transaction_id": transaction_id
                    }
                )
                self.send_message_callback(message)
        
        with self.lock:
            self.transactions[transaction_id]["state"] = TransactionState.ABORTED
            self.transactions[transaction_id]["end_time"] = time.time()
        
        logger.info(f"Transaction {transaction_id}: Aborted")
    
    def handle_prepare(self, transaction_id: str, operations: List[Dict[str, Any]]) -> str:
        """Handle PREPARE message (participant side)."""
        # Validate operations
        if self._validate_operations(operations):
            with self.lock:
                self.transactions[transaction_id] = {
                    "operations": operations,
                    "state": TransactionState.WAIT,
                    "start_time": time.time()
                }
            logger.info(f"Transaction {transaction_id}: Prepared (vote: COMMIT)")
            return "COMMIT"
        else:
            logger.info(f"Transaction {transaction_id}: Cannot prepare (vote: ABORT)")
            return "ABORT"
    
    def handle_commit(self, transaction_id: str) -> bool:
        """Handle COMMIT message (participant side)."""
        with self.lock:
            if transaction_id in self.transactions:
                self.transactions[transaction_id]["state"] = TransactionState.COMMITTED
                self.transactions[transaction_id]["end_time"] = time.time()
        
        # Execute operations
        operations = self.transactions[transaction_id]["operations"]
        success = self._execute_operations(operations)
        
        logger.info(f"Transaction {transaction_id}: Committed")
        return success
    
    def handle_abort(self, transaction_id: str):
        """Handle ABORT message (participant side)."""
        with self.lock:
            if transaction_id in self.transactions:
                self.transactions[transaction_id]["state"] = TransactionState.ABORTED
                self.transactions[transaction_id]["end_time"] = time.time()
        
        logger.info(f"Transaction {transaction_id}: Aborted")
    
    def _validate_operations(self, operations: List[Dict[str, Any]]) -> bool:
        """Validate operations (placeholder - implement based on your needs)."""
        # In a real implementation, this would validate operations
        return True
    
    def _execute_operations(self, operations: List[Dict[str, Any]]) -> bool:
        """Execute operations (placeholder - implement based on your needs)."""
        # In a real implementation, this would execute operations
        for op in operations:
            logger.debug(f"Executing operation: {op}")
        return True
    
    def record_vote(self, transaction_id: str, participant_id: str, vote: str):
        """Record a vote from a participant."""
        with self.lock:
            if transaction_id not in self.votes:
                self.votes[transaction_id] = {}
            self.votes[transaction_id][participant_id] = vote
    
    def get_transaction_state(self, transaction_id: str) -> Optional[TransactionState]:
        """Get the state of a transaction."""
        with self.lock:
            if transaction_id in self.transactions:
                return self.transactions[transaction_id]["state"]
            return None
