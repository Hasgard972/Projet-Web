FROM python:3.13-slim

# Installation des dépendances système nécessaires pour psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Définir le dossier de travail
WORKDIR /app

# Copier les dépendances Python et les installer
# (Copier uniquement requirements.txt d'abord profite du cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste du projet dans le conteneur
COPY . .

# Copier le script d'entrée et le rendre exécutable
# C'est une étape cruciale, sinon Docker ne pourra pas l'exécuter
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Définir le script comme point d'entrée du conteneur
# Docker exécutera ce script à chaque `docker run`
# ENTRYPOINT ["/app/entrypoint.sh"]