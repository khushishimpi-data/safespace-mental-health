FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    streamlit==1.55.0 \
    requests==2.31.0 \
    httpx==0.25.2 \
    python-dotenv==1.0.0 \
    pydantic==2.5.0 \
    pandas==2.1.3 \
    numpy==1.26.2 \
    plotly==5.17.0

# Copy application code
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
