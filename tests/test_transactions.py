"""Tests for transaction management."""

import unittest
from src.transactions.transaction_manager import TransactionManager
from src.transactions.two_phase_commit import TwoPhaseCommit, TransactionState


class TestTransactionManager(unittest.TestCase):
    """Test transaction manager."""
    
    def test_begin_transaction(self):
        """Test beginning a transaction."""
        manager = TransactionManager("node-1")
        participants = ["node-2", "node-3"]
        transaction_id = manager.begin_transaction(participants)
        self.assertIsNotNone(transaction_id)
        self.assertIn(transaction_id, manager.active_transactions)


class TestTwoPhaseCommit(unittest.TestCase):
    """Test 2PC protocol."""
    
    def test_2pc_states(self):
        """Test 2PC transaction states."""
        two_pc = TwoPhaseCommit("node-1")
        # Test initial state
        self.assertIsNotNone(two_pc.transactions)


if __name__ == "__main__":
    unittest.main()
