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


def download_model_from_s3(bucket_name: str, s3_prefix: str, local_path: str) -> bool:
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

        # List all objects with the prefix
        paginator = s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix)

        for page in pages:
            if "Contents" not in page:
                continue

            for obj in page["Contents"]:
                # Get the object key
                s3_key = obj["Key"]

                # Create the local file path
                # Remove the prefix from the key to get the relative path
                relative_path = s3_key[len(s3_prefix) :].lstrip("/")
                local_file_path = os.path.join(local_path, relative_path)

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
        return

    logger.info(f"Model directory {MODEL_DIR} not found. Downloading from S3...")
    success = download_model_from_s3(BUCKET_NAME, S3_PREFIX, MODEL_DIR)

    if not success:
        logger.error("Failed to download model from S3")
        raise Exception("Model download failed")
