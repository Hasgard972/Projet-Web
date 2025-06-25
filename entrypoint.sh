#!/bin/sh

# Cette ligne assure que le script s'arrêtera si une commande échoue
set -e

# Afficher un message pour indiquer ce qui se passe
echo "--- Initialisation de la base de données ---"
# Exécuter la commande d'initialisation de la base de données
flask init-db

# Afficher un message avant de lancer le serveur
echo "--- Démarrage du serveur Web Flask ---"
# Lancer le serveur Flask.
# "exec" est important : il remplace le processus du script par celui de Flask,
# ce qui permet au conteneur de s'arrêter proprement.
exec flask run --host=0.0.0.0