import socket
import threading
import json
import os
import logging
from .crypto import CryptoHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('vpm-server')

class VPMServer:
    def __init__(self, host='0.0.0.0', port=8080, password=None):
        self.host = host
        self.port = port
        self.clients = {}
        self.client_lock = threading.Lock()
        self.running = False
        self.server_socket = None
        
        # Initialize crypto with password or random key
        self.crypto = CryptoHandler()
        if password:
            self.salt = self.crypto.generate_key_from_password(password)
        
    def start(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        logger.info(f"Server started on {self.host}:{self.port}")
        
        # Accept client connections in a loop
        accept_thread = threading.Thread(target=self.accept_clients)
        accept_thread.daemon = True
        accept_thread.start()
        
        return accept_thread
    
    def accept_clients(self):
        """Accept new client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"New connection from {address}")
                
                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket, address):
        """Handle communication with a client"""
        client_id = f"{address[0]}:{address[1]}"
        
        try:
            # Authenticate the client
            if not self._authenticate_client(client_socket):
                logger.warning(f"Failed authentication from {client_id}")
                client_socket.close()
                return
                
            # Register the client
            with self.client_lock:
                self.clients[client_id] = {
                    "socket": client_socket,
                    "address": address,
                    "crypto": self.crypto  # Each client uses the same crypto for now
                }
            
            # Handle client messages
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                # Decrypt and process the message
                decrypted = self.crypto.decrypt(data.decode('utf-8'))
                self._process_client_message(client_id, json.loads(decrypted))
                
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up client connection
            with self.client_lock:
                if client_id in self.clients:
                    del self.clients[client_id]
            try:
                client_socket.close()
            except:
                pass
            logger.info(f"Client {client_id} disconnected")
    
    def _authenticate_client(self, client_socket):
        """Verify client has the correct authentication credentials"""
        # Implement a challenge-response authentication
        challenge = os.urandom(32)
        client_socket.sendall(challenge)
        
        response = client_socket.recv(4096)
        # In a real implementation, verify the response
        # For now, just accept any response
        return True
        
    def _process_client_message(self, client_id, message):
        """Process messages from clients"""
        logger.info(f"Message from {client_id}: {message}")
        # Handle different message types here
        
    def send_to_client(self, client_id, message):
        """Send an encrypted message to a specific client"""
        if client_id not in self.clients:
            logger.warning(f"Client {client_id} not found")
            return False
            
        encrypted = self.crypto.encrypt(json.dumps(message))
        try:
            self.clients[client_id]["socket"].sendall(encrypted.encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
            return False
    
    def broadcast(self, message, exclude=None):
        """Send a message to all connected clients"""
        exclude = exclude or []
        with self.client_lock:
            for client_id, client in self.clients.items():
                if client_id not in exclude:
                    self.send_to_client(client_id, message)
    
    def stop(self):
        """Stop the server and close all connections"""
        self.running = False
        
        # Close all client connections
        with self.client_lock:
            for client_id, client in self.clients.items():
                try:
                    client["socket"].close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("Server stopped")
