FROM python:3.12-slim

# Install C++ build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Build C++ extension
RUN python setup.py build_ext --inplace

EXPOSE 5000
CMD ["python", "app.py"]
