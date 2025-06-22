import logging

# Configure logging
logging.basicConfig(
    filename='app.log',            # log to file
    level=logging.INFO,            # minimum level to log
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("app_logger")
