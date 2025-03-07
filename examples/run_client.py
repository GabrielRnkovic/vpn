import sys
import os
import time
import logging

# Add parent directory to path to import vpm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vpm import VPMClient

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and connect the client
    client = VPMClient(
        server_host='127.0.0.1',  # Connect to localhost for testing
        server_port=8080,
        password='secret_password'
    )
    
    if not client.connect():
        print("Failed to connect to the server.")
        return
    
    try:
        # Send a test message
        client.send_message({
            "type": "hello",
            "content": "Hello from client!"
        })
        
        # Keep the client running
        while client.connected:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Shutting down client...")
    finally:
        client.disconnect()
        
if __name__ == "__main__":
    main()
