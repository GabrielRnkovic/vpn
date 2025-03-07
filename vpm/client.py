import socket
import threading
import json
import time
import logging
from .crypto import CryptoHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('vpm-client')

class VPMClient:
    def __init__(self, server_host, server_port=8080, password=None):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.running = False
        
        # Initialize crypto
        self.crypto = CryptoHandler()
        if password:
            # In a real implementation, we'd get the salt from the server
            # For simplicity, using a fixed salt for now
            self.crypto.generate_key_from_password(password, b'fixed_salt_for_demo')
        
    def connect(self):
        """Connect to the VPM server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            self.running = True
            
            # Start a thread to receive messages
            receive_thread = threading.Thread(target=self._receive_loop)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Authenticate with the server
            if not self._authenticate():
                logger.error("Failed to authenticate with server")
                self.disconnect()
                return False
                
            logger.info(f"Connected to {self.server_host}:{self.server_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.connected = False
            return False
    
    def _receive_loop(self):
        """Continuously receive messages from the server"""
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    logger.info("Connection closed by server")
                    break
                    
                decrypted = self.crypto.decrypt(data.decode('utf-8'))
                self._handle_message(json.loads(decrypted))
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error receiving data: {e}")
                    break
        
        self.connected = False
    
    def _authenticate(self):
        """Authenticate with the server"""
        # In a real implementation, handle the challenge-response
        challenge = self.socket.recv(4096)
        # Send some response for now
        self.socket.sendall(b"authentication-response")
        return True
    
    def _handle_message(self, message):
        """Process messages from the server"""
        logger.info(f"Received message: {message}")
        # Implement message handling logic here
    
    def send_message(self, message):
        """Send an encrypted message to the server"""
        if not self.connected:
            logger.warning("Not connected to server")
            return False
            
        try:
            encrypted = self.crypto.encrypt(json.dumps(message))
            self.socket.sendall(encrypted.encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            
        self.connected = False
        logger.info("Disconnected from server")
