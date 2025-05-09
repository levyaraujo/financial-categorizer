#!/bin/bash
set -e

# echo "Starting model download..."
python src/download_model.py

if [ $? -eq 0 ]; then
    echo "Model download completed successfully"
    echo "Starting FastAPI application..."
    exec uvicorn main:app --host 0.0.0.0 --port 8000
else
    echo "Model download failed"
    exit 1
fi