# Use Python 3.11 as the base image
FROM python:3.15-slim

# Install Tkinter dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    tk-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn

# Now copy **everything** from the project root into /app
COPY . /app

# Expose the port that FastAPI will run on
EXPOSE 8000

ENV PYTHONPATH=/app/src

# Command to run the application
CMD ["python", "-m", "uvicorn", "src.controller:app", "--host", "0.0.0.0", "--port", "8000"]