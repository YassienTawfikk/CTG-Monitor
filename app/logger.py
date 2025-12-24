import logging
import os

def setup_logging():
    log_file = "app.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging initialized")

def get_logger(name):
    return logging.getLogger(name)
