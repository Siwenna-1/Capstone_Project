"""RPC (Remote Procedure Call) implementation."""

import socket
import json
import threading
import time
from typing import Callable, Dict, Any, Optional
from queue import Queue
import logging

from ..common.messages import Message, MessageType
from ..common.logger import setup_logger

logger = setup_logger(__name__)


class RPCServer:
    """RPC Server for handling remote procedure calls."""
    
    def __init__(self, host: str = "localhost", port: int = 8000, node_id: str = "server"):
        self.host = host
        self.port = port
        self.node_id = node_id
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.handlers: Dict[str, Callable] = {}
        self.thread: Optional[threading.Thread] = None
        
    def register_handler(self, method: str, handler: Callable):
        """Register a handler for an RPC method."""
        self.handlers[method] = handler
        logger.info(f"Registered RPC handler for method: {method}")
    
    def start(self):
        """Start the RPC server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        
        self.thread = threading.Thread(target=self._accept_connections, daemon=True)
        self.thread.start()
        logger.info(f"RPC Server started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the RPC server."""
        self.running = False
        if self.socket:
            self.socket.close()
        logger.info("RPC Server stopped")
    
    def _accept_connections(self):
        """Accept incoming connections."""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle a client connection."""
        try:
            data = client_socket.recv(4096)
            if data:
                request = json.loads(data.decode())
                response = self._process_request(request)
                client_socket.send(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method in self.handlers:
            try:
                result = self.handlers[method](**params)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            except Exception as e:
                logger.error(f"Error executing RPC method {method}: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }


class RPCClient:
    """RPC Client for making remote procedure calls."""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.timeout = 5.0
    
    def call(self, method: str, **params) -> Any:
        """Make an RPC call."""
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
            "params": params
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            sock.send(json.dumps(request).encode())
            
            response_data = sock.recv(4096)
            sock.close()
            
            response = json.loads(response_data.decode())
            
            if "error" in response:
                raise Exception(f"RPC Error: {response['error']['message']}")
            
            return response.get("result")
        except socket.timeout:
            raise Exception(f"RPC call timeout to {self.host}:{self.port}")
        except Exception as e:
            raise Exception(f"RPC call failed: {e}")
    
    def async_call(self, method: str, callback: Callable, **params):
        """Make an asynchronous RPC call."""
        def _async_call():
            try:
                result = self.call(method, **params)
                callback(result, None)
            except Exception as e:
                callback(None, e)
        
        thread = threading.Thread(target=_async_call, daemon=True)
        thread.start()
