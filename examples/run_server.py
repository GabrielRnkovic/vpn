import sys
import os
import time
import logging

# Add parent directory to path to import vpm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vpm import VPMServer

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the server
    server = VPMServer(host='0.0.0.0', port=8080, password='secret_password')
    server_thread = server.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server.stop()
        
if __name__ == "__main__":
    main()
