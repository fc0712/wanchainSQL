import logging
import sys

log_Format = "%(levelname)s %(asctime)s - %(message)s"
time_format = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(
    level=logging.INFO, format=log_Format, stream=sys.stdout, datefmt=time_format
)
logger = logging.getLogger(__name__)
