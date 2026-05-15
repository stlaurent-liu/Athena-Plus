import logging
import os

from athena.config import settings

# Create logs directory if not exists
if settings.data_dir:
    os.makedirs(os.path.join(settings.data_dir, "logs"), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(settings.data_dir, "logs", "athena.log"), encoding='utf-8')
    ] if settings.data_dir else [logging.StreamHandler()]
)

logger = logging.getLogger("athena")
