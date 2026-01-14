"""Client-server messaging implementation."""

import socket
import json
import threading
import time
from typing import Callable, Dict, Any, Optional, List
from queue import Queue
import logging

from ..common.messages import Message, MessageType
from ..common.logger import setup_logger

logger = setup_logger(__name__)


class MessageQueue:
    """Message queue for reliable message delivery."""
    
    def __init__(self, queue_id: str):
        self.queue_id = queue_id
        self.messages: Queue = Queue()
        self.acknowledged: Dict[str, bool] = {}
        self.pending: Dict[str, Message] = {}
    
    def enqueue(self, message: Message):
        """Add a message to the queue."""
        self.messages.put(message)
        if message.msg_id not in self.acknowledged:
            self.pending[message.msg_id] = message
            self.acknowledged[message.msg_id] = False
    
    def dequeue(self, timeout: float = None) -> Optional[Message]:
        """Get a message from the queue."""
        try:
            return self.messages.get(timeout=timeout)
        except:
            return None
    
    def acknowledge(self, message_id: str):
        """Acknowledge a message."""
        self.acknowledged[message_id] = True
        if message_id in self.pending:
            del self.pending[message_id]
    
    def get_pending(self) -> List[Message]:
        """Get all pending (unacknowledged) messages."""
        return [msg for msg_id, msg in self.pending.items() 
                if not self.acknowledged.get(msg_id, False)]


class MessagingServer:
    """Messaging server for client-server communication."""
    
    def __init__(self, host: str = "localhost", port: int = 9000, node_id: str = "server"):
        self.host = host
        self.port = port
        self.node_id = node_id
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.clients: Dict[str, socket.socket] = {}
        self.message_queue = MessageQueue(node_id)
        self.thread: Optional[threading.Thread] = None
    
    def register_handler(self, msg_type: MessageType, handler: Callable):
        """Register a handler for a message type."""
        self.message_handlers[msg_type] = handler
        logger.info(f"Registered handler for message type: {msg_type.value}")
    
    def start(self):
        """Start the messaging server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        
        self.thread = threading.Thread(target=self._accept_connections, daemon=True)
        self.thread.start()
        logger.info(f"Messaging Server started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the messaging server."""
        self.running = False
        if self.socket:
            self.socket.close()
        for client_socket in self.clients.values():
            client_socket.close()
        logger.info("Messaging Server stopped")
    
    def send_message(self, client_id: str, message: Message):
        """Send a message to a client."""
        if client_id in self.clients:
            try:
                client_socket = self.clients[client_id]
                client_socket.send(message.to_json().encode() + b'\n')
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                del self.clients[client_id]
        else:
            self.message_queue.enqueue(message)
    
    def _accept_connections(self):
        """Accept incoming connections."""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                client_id = f"{address[0]}:{address[1]}"
                self.clients[client_id] = client_socket
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_id),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
    
    def _handle_client(self, client_socket: socket.socket, client_id: str):
        """Handle a client connection."""
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                messages = data.decode().strip().split('\n')
                for msg_str in messages:
                    if msg_str:
                        message = Message.from_json(msg_str)
                        self._process_message(message, client_id)
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            client_socket.close()
    
    def _process_message(self, message: Message, client_id: str):
        """Process an incoming message."""
        msg_type = message.msg_type
        
        if msg_type in self.message_handlers:
            try:
                self.message_handlers[msg_type](message, client_id)
            except Exception as e:
                logger.error(f"Error processing message {message.msg_id}: {e}")


class MessagingClient:
    """Messaging client for sending and receiving messages."""
    
    def __init__(self, host: str = "localhost", port: int = 9000, client_id: str = "client"):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.receive_thread: Optional[threading.Thread] = None
    
    def connect(self):
        """Connect to the messaging server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            logger.info(f"Connected to messaging server at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Error connecting to server: {e}")
            self.connected = False
    
    def disconnect(self):
        """Disconnect from the messaging server."""
        self.connected = False
        if self.socket:
            self.socket.close()
        logger.info("Disconnected from messaging server")
    
    def send_message(self, message: Message):
        """Send a message to the server."""
        if self.connected and self.socket:
            try:
                self.socket.send(message.to_json().encode() + b'\n')
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                self.connected = False
    
    def register_handler(self, msg_type: MessageType, handler: Callable):
        """Register a handler for a message type."""
        self.message_handlers[msg_type] = handler
    
    def _receive_messages(self):
        """Receive messages from the server."""
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                buffer += data.decode()
                while '\n' in buffer:
                    msg_str, buffer = buffer.split('\n', 1)
                    if msg_str:
                        message = Message.from_json(msg_str)
                        self._process_message(message)
            except Exception as e:
                if self.connected:
                    logger.error(f"Error receiving messages: {e}")
                break
    
    def _process_message(self, message: Message):
        """Process an incoming message."""
        msg_type = message.msg_type
        
        if msg_type in self.message_handlers:
            try:
                self.message_handlers[msg_type](message)
            except Exception as e:
                logger.error(f"Error processing message {message.msg_id}: {e}")
