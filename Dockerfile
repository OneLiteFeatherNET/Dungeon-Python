FROM python:3.15-slim

WORKDIR /app

# Install the runtime dependencies first to leverage the Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The API only needs the source code
COPY src ./src

# Run the application as an unprivileged user
RUN useradd --create-home --uid 1000 app
USER app

# Expose the port that FastAPI will run on
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "controller:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
