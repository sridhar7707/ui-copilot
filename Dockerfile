FROM python:3.11-slim

WORKDIR /app

# Build tools for C-extension wheels + OpenCV runtime libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: CLIP similarity scoring (Module 3b).
# sentence-transformers + PyTorch adds ~2 GB — install separately so a
# failure here never breaks the core app (benchmark returns available:false).
RUN pip install --no-cache-dir sentence-transformers || \
    echo "sentence-transformers unavailable — benchmark scoring disabled"

COPY . .

# HuggingFace Spaces persistent storage mounts at /data
ENV DB_PATH=/data/uicopilot.db

EXPOSE 7860

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
