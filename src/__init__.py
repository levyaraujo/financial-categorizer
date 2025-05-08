import os
import logging
from dotenv import load_dotenv

from src.download_model import main

# Load environment variables from .env file
load_dotenv()

main()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required environment variables
REQUIRED_ENV_VARS = ["ACCESS_KEY", "SECRET_ACCESS_KEY", "BUCKET_NAME", "S3_PREFIX"]

# Default model path based on Fly.io volume mount
DEFAULT_MODEL_PATH = "/data/model"

# Check if all required environment variables are set
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )

# Set default model path if not provided
if not os.getenv("MODEL_PATH"):
    os.environ["MODEL_PATH"] = DEFAULT_MODEL_PATH
    logger.info(f"Using default model path: {DEFAULT_MODEL_PATH}")

# Ensure model directory exists
os.makedirs(os.getenv("MODEL_PATH"), exist_ok=True)
