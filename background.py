from flask import Flask
from flask import request
from threading import Thread
import time
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port)

def health_check():
    """Run health check in a separate thread"""
    port = int(os.environ.get('PORT', 8080))
    while True:
        try:
            response = requests.get(f"http://localhost:{port}/")
            if response.status_code == 200:
                logger.debug("Health check successful")
            else:
                logger.warning(f"Health check failed with status code: {response.status_code}")
            time.sleep(60)  # Check every 60 seconds
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during health check: {e}")
            time.sleep(60)  # Wait and retry

def keep_alive():
    """Start Flask server and health check in separate threads"""
    server_thread = Thread(target=run)
    health_thread = Thread(target=health_check)

    server_thread.start()
    logger.info("Flask server thread started")

    health_thread.start()
    logger.info("Health check thread started")

if __name__ == "__main__":
    keep_alive()