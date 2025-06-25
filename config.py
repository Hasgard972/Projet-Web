# config.py

import os

class Config:
    # --- AJOUT DE LA LIGNE SUIVANTE ---
    # Charge la clé secrète depuis une variable d'environnement.
    # Fournit une valeur par défaut 'dev' pour faciliter le développement,
    # mais il FAUT la changer en production.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    # Le reste de la configuration ne change pas
    DB_NAME = os.getenv("DB_NAME", "api8inf349")
    DB_USER = os.getenv("DB_USER", "user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "pass")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")

    # Pour Peewee
    DB_SETTINGS = {
        'name': DB_NAME,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'port': DB_PORT
    }