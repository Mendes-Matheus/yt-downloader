FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install jinja2

COPY app/ ./app/

# Criar diretórios necessários
RUN mkdir -p /app/downloads /app/static /app/templates

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]