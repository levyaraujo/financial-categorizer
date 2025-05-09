import os
import boto3
from botocore.exceptions import ClientError
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

required_files = [
    "config.json",
    "rng_state.pth",
    "scheduler.pt",
    "trainer_state.json",
    "training_args.bin",
    "model.safetensors",
    "optimizer.pt",
]


def download_model_from_s3(
    bucket_name: str, s3_prefix: str, local_path: str, file: str
) -> bool:
    """
    Download all files with a specific prefix from S3 bucket to local path.

    Args:
        bucket_name (str): Name of the S3 bucket
        s3_prefix (str): Prefix/path of the objects in S3
        local_path (str): Local path where the model should be saved

    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        # Configure AWS credentials
        aws_access_key = os.getenv("ACCESS_KEY")
        aws_secret_key = os.getenv("SECRET_ACCESS_KEY")

        if not aws_access_key or not aws_secret_key:
            logger.error("AWS credentials not found in environment variables")
            return False

        s3_client = boto3.client(
            "s3", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key
        )

        # Create directory if it doesn't exist
        os.makedirs(local_path, exist_ok=True)

        s3_key = f"{s3_prefix}/{file}"

        local_file_path = os.path.join(local_path, file)

        # Create directory for the file if it doesn't exist
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        logger.info(f"Downloading {s3_key} to {local_file_path}")
        s3_client.download_file(bucket_name, s3_key, local_file_path)

        logger.info(f"Successfully downloaded all files to {local_path}")
        return True

    except ClientError as e:
        logger.error(f"Error downloading from S3: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False


def main():
    MODEL_DIR = os.getenv("MODEL_PATH")
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    S3_PREFIX = os.getenv("S3_PREFIX")

    if os.path.exists(MODEL_DIR):
        logger.info(f"Model directory {MODEL_DIR} already exists")

    os.makedirs(MODEL_DIR, exist_ok=True)

    logger.info(f"Model directory {MODEL_DIR} not found. Downloading from S3...")

    for file in required_files:
        if os.path.exists(os.path.join(MODEL_DIR, file)):
            logger.info(f"File {file} already exists in {MODEL_DIR}")
            continue
        download_model_from_s3(BUCKET_NAME, S3_PREFIX, MODEL_DIR, file)
        assert os.path.exists(os.path.join(MODEL_DIR, file)), (
            f"File {file} not found after download"
        )
        logger.info(f"File {file} successfully downloaded to {MODEL_DIR}")
