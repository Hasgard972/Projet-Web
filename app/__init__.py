# app/__init__.py

from flask import Flask
from .routes import bp as api_blueprint
# Importez db pour que la commande CLI puisse s'y connecter
from .models import db, Product, Order, OrderProduct
from .utils import fetch_and_store_products
import click


def create_app():
    # Le chemin du template sera automatiquement trouvé s'il est dans le dossier 'app'
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")

    # --- CORRECTION ---
    # On retire la ligne suivante, car notre objet `db` n'est pas une extension Flask.
    # db.init_app(app)  <-- SUPPRIMER CETTE LIGNE

    # Enregistrer le blueprint
    app.register_blueprint(api_blueprint)

    # Ajouter les commandes CLI à l'application
    @app.cli.command("init-db")
    def init_db_command():
        """Créer les tables et importer les produits."""
        try:
            # Assurer la connexion à la BDD avant toute opération
            if db.is_closed():
                db.connect()

            click.echo("Création des tables...")
            db.create_tables([Product, Order, OrderProduct])
            click.echo("✅ Tables créées.")

            click.echo("Importation des produits...")
            fetch_and_store_products()
            click.echo("✅ Produits importés.")

        except Exception as e:
            click.echo(f"❌ Erreur lors de l'initialisation de la BDD: {e}")
        finally:
            # Toujours fermer la connexion après l'opération CLI
            if not db.is_closed():
                db.close()

    # Gestion de la connexion BDD avant et après chaque requête
    # C'est la manière "manuelle" de faire ce que Flask-Peewee ferait automatiquement
    @app.before_request
    def _db_connect():
        if db.is_closed():
            db.connect()

    @app.after_request
    def _db_close(exc):
        if not db.is_closed():
            db.close()
        return exc

    return app