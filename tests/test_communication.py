"""Tests for communication components."""

import unittest
import time
from src.communication.rpc import RPCServer, RPCClient
from src.communication.messaging import MessagingServer, MessagingClient
from src.communication.dsm import DistributedSharedMemory
from src.communication.event_ordering import VectorClock, EventOrderer


class TestRPC(unittest.TestCase):
    """Test RPC functionality."""
    
    def test_rpc_server_client(self):
        """Test RPC server and client."""
        server = RPCServer("localhost", 8000, "test-server")
        
        def handler(value):
            return value * 2
        
        server.register_handler("double", handler)
        server.start()
        
        time.sleep(0.1)  # Wait for server to start
        
        client = RPCClient("localhost", 8000)
        result = client.call("double", value=5)
        
        self.assertEqual(result, 10)
        server.stop()


class TestDSM(unittest.TestCase):
    """Test Distributed Shared Memory."""
    
    def test_dsm_set_get(self):
        """Test DSM set and get operations."""
        dsm = DistributedSharedMemory("node-1")
        dsm.set("key1", "value1")
        self.assertEqual(dsm.get("key1"), "value1")
    
    def test_dsm_vector_clock(self):
        """Test DSM vector clock."""
        dsm = DistributedSharedMemory("node-1")
        dsm.set("key1", "value1")
        clock = dsm.get_vector_clock()
        self.assertIn("node-1", clock)


class TestVectorClock(unittest.TestCase):
    """Test vector clock."""
    
    def test_vector_clock_tick(self):
        """Test vector clock ticking."""
        clock = VectorClock("node-1")
        clock.tick()
        clock_values = clock.get_clock()
        self.assertEqual(clock_values["node-1"], 1)
    
    def test_vector_clock_happened_before(self):
        """Test happened-before relationship."""
        clock1 = VectorClock("node-1")
        clock1.tick()
        clock1.tick()
        
        clock2 = VectorClock("node-2")
        clock2.update(clock1.get_clock())
        clock2.tick()
        
        self.assertTrue(clock1.happened_before(clock2.get_clock()))


if __name__ == "__main__":
    unittest.main()
