# Use a slim Python image to keep the size down
FROM python:3.10-slim

# 1. Install System Dependencies
# We need build-essential and g++ to compile llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libstdc++6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Set the working directory
WORKDIR /app

# 3. Handle Python Dependencies
# We copy requirements first to leverage Docker's cache
COPY requirements.txt .

# Install dependencies
# Note: We set CMAKE_ARGS to ensure llama-cpp builds for CPU (Railway standard)
RUN CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" \
    pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application
COPY . .

# 5. Create a directory for the model
RUN mkdir -p models

# 6. Set Environment Variables
# These tell your app where it's running
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV MODEL_PATH="models/smollm2-135m-instruct-q8_0.gguf"

# 7. Expose the port FastAPI will run on
EXPOSE 8000

# 8. The Launch Command
# First download the model, then start the server
CMD python download_model.py && uvicorn main:app --host 0.0.0.0 --port ${PORT}