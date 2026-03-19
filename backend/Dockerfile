FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-multipart==0.0.6 \
    sqlalchemy==2.0.48 \
    psycopg2-binary==2.9.9 \
    python-jose==3.3.0 \
    passlib==1.7.4 \
    python-dotenv==1.0.0 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    langchain==0.1.0 \
    openai==1.3.8 \
    groq==0.4.2 \
    requests==2.31.0 \
    httpx==0.25.2 \
    pyttsx3==2.90

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]