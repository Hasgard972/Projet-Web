# inf349.py

from app import create_app

# Créer l'application en utilisant la factory
app = create_app()

if __name__ == "__main__":
    # Note: `flask run` est la manière recommandée pour lancer en développement
    app.run(host="0.0.0.0", port=5000)