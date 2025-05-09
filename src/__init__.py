import os
import logging
from dotenv import load_dotenv

from src.download_model import main

# Load environment variables from .env file
load_dotenv()

main()
