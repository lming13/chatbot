# Utiliser une base Python 3.9 sur Debian
FROM python:3.9-slim

# Installer les dépendances nécessaires
RUN apt update && apt install -y curl unzip && rm -rf /var/lib/apt/lists/*

# Installer Ollama proprement
RUN curl -fsSL https://ollama.com/install.sh | sh

# Vérifier que Ollama est bien installé
RUN /usr/local/bin/ollama --version

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY requirements.txt .
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Démarrer Ollama avant FastAPI et éviter le problème de port bloqué
CMD ["sh", "-c", "kill -9 $(lsof -t -i:8000) 2>/dev/null || true && ollama serve & sleep 5 && ollama pull mistral && uvicorn main:app --host 0.0.0.0 --port 8000"]
