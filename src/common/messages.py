"""Message definitions for distributed system communication."""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional
import json
import time
import uuid


class MessageType(Enum):
    """Types of messages in the system."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    TRANSACTION_PREPARE = "transaction_prepare"
    TRANSACTION_COMMIT = "transaction_commit"
    TRANSACTION_ABORT = "transaction_abort"
    TRANSACTION_ACK = "transaction_ack"
    REPLICATION_UPDATE = "replication_update"
    FAILOVER_NOTIFICATION = "failover_notification"
    LOAD_UPDATE = "load_update"


class NodeType(Enum):
    """Types of nodes in the system."""
    EDGE = "edge"
    CORE = "core"
    CLOUD = "cloud"
    CLIENT = "client"


@dataclass
class Message:
    """Base message class for all system communications."""
    msg_id: str
    msg_type: MessageType
    sender_id: str
    receiver_id: Optional[str]
    timestamp: float
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type.value,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "correlation_id": self.correlation_id
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            msg_id=data["msg_id"],
            msg_type=MessageType(data["msg_type"]),
            sender_id=data["sender_id"],
            receiver_id=data.get("receiver_id"),
            timestamp=data["timestamp"],
            payload=data["payload"],
            correlation_id=data.get("correlation_id")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def create_request(cls, sender_id: str, receiver_id: str, payload: Dict[str, Any]) -> 'Message':
        """Create a request message."""
        return cls(
            msg_id=str(uuid.uuid4()),
            msg_type=MessageType.REQUEST,
            sender_id=sender_id,
            receiver_id=receiver_id,
            timestamp=time.time(),
            payload=payload
        )
    
    @classmethod
    def create_response(cls, sender_id: str, receiver_id: str, payload: Dict[str, Any], 
                       correlation_id: str) -> 'Message':
        """Create a response message."""
        return cls(
            msg_id=str(uuid.uuid4()),
            msg_type=MessageType.RESPONSE,
            sender_id=sender_id,
            receiver_id=receiver_id,
            timestamp=time.time(),
            payload=payload,
            correlation_id=correlation_id
        )
    
    @classmethod
    def create_heartbeat(cls, sender_id: str) -> 'Message':
        """Create a heartbeat message."""
        return cls(
            msg_id=str(uuid.uuid4()),
            msg_type=MessageType.HEARTBEAT,
            sender_id=sender_id,
            receiver_id=None,
            timestamp=time.time(),
            payload={"status": "alive"}
        )


@dataclass
class TransactionMessage:
    """Message for transaction operations."""
    transaction_id: str
    operation: str  # "prepare", "commit", "abort", "ack"
    node_id: str
    timestamp: float
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transaction_id": self.transaction_id,
            "operation": self.operation,
            "node_id": self.node_id,
            "timestamp": self.timestamp,
            "data": self.data
        }
