"""Event ordering using vector clocks."""

import threading
from typing import Dict, List, Tuple
import logging

from ..common.logger import setup_logger

logger = setup_logger(__name__)


class VectorClock:
    """Vector clock for event ordering."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.clock: Dict[str, int] = {node_id: 0}
        self.lock = threading.Lock()
    
    def tick(self):
        """Increment the local clock."""
        with self.lock:
            self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
    
    def update(self, other_clock: Dict[str, int]):
        """Update this clock with another clock (max of each component)."""
        with self.lock:
            for node_id, time in other_clock.items():
                self.clock[node_id] = max(self.clock.get(node_id, 0), time)
    
    def get_clock(self) -> Dict[str, int]:
        """Get a copy of the clock."""
        with self.lock:
            return self.clock.copy()
    
    def set_clock(self, clock: Dict[str, int]):
        """Set the clock."""
        with self.lock:
            self.clock = clock.copy()
    
    def happened_before(self, other_clock: Dict[str, int]) -> bool:
        """Check if this clock happened before another clock."""
        with self.lock:
            less_than = False
            for node_id in set(self.clock.keys()) | set(other_clock.keys()):
                local_time = self.clock.get(node_id, 0)
                other_time = other_clock.get(node_id, 0)
                
                if local_time < other_time:
                    less_than = True
                elif local_time > other_time:
                    return False
            
            return less_than
    
    def concurrent(self, other_clock: Dict[str, int]) -> bool:
        """Check if two clocks are concurrent."""
        return not self.happened_before(other_clock) and not self._other_happened_before(other_clock)
    
    def _other_happened_before(self, other_clock: Dict[str, int]) -> bool:
        """Check if the other clock happened before this clock."""
        with self.lock:
            less_than = False
            for node_id in set(self.clock.keys()) | set(other_clock.keys()):
                local_time = self.clock.get(node_id, 0)
                other_time = other_clock.get(node_id, 0)
                
                if other_time < local_time:
                    less_than = True
                elif other_time > local_time:
                    return False
            
            return less_than
    
    def __str__(self):
        return str(self.get_clock())


class EventOrderer:
    """Event orderer using vector clocks."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.vector_clock = VectorClock(node_id)
        self.events: List[Tuple[Dict[str, int], str, any]] = []  # (clock, event_id, data)
        self.lock = threading.Lock()
    
    def create_event(self, event_id: str, data: any) -> Dict[str, int]:
        """Create a new event and return its vector clock."""
        with self.lock:
            self.vector_clock.tick()
            clock = self.vector_clock.get_clock()
            self.events.append((clock, event_id, data))
            return clock
    
    def receive_event(self, event_id: str, data: any, clock: Dict[str, int]):
        """Receive an event from another node."""
        with self.lock:
            self.vector_clock.update(clock)
            self.events.append((clock.copy(), event_id, data))
            # Sort events by vector clock
            self._sort_events()
    
    def _sort_events(self):
        """Sort events by their vector clocks."""
        # Simple sorting: events are ordered by their vector clocks
        # This is a simplified version - a full implementation would use
        # topological sorting for causal ordering
        pass
    
    def get_causal_order(self) -> List[Tuple[str, any]]:
        """Get events in causal order."""
        with self.lock:
            # Sort events by vector clock
            sorted_events = sorted(self.events, key=lambda x: self._clock_to_tuple(x[0]))
            return [(event_id, data) for _, event_id, data in sorted_events]
    
    def _clock_to_tuple(self, clock: Dict[str, int]) -> Tuple:
        """Convert a clock to a tuple for sorting."""
        # Convert clock to a tuple for comparison
        sorted_items = sorted(clock.items())
        return tuple(time for _, time in sorted_items)
    
    def get_vector_clock(self) -> Dict[str, int]:
        """Get the current vector clock."""
        return self.vector_clock.get_clock()
