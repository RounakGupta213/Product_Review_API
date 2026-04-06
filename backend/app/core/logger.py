import logging
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_filename = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
