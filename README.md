# API de Commande de Produits

Cette API développée avec Flask permet :
- d’afficher la liste des produits disponibles,
- de passer une commande,
- de consulter le détail d’une commande.

## Lancer le projet

### Prérequis

- Python 3.10 ou supérieur
- `pip` ou `poetry`
- Environnement virtuel recommandé (ex. : `.venv`)

### Installation

1. Cloner le dépôt ou extraire l’archive :
   ```bash
   git clone <url_du_projet>
   cd 1_Projet_API
   ```

2. Activer l’environnement virtuel (si non déjà actif) :
   ```bash
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Lancer l’API :
   ```bash
   flask --app app/routes run
   ```

---

## Endpoints

### `GET /`

Retourne la liste des produits en stock.

#### Exemple de réponse

```json
{
  "products": [
    {
      "id": 1,
      "name": "Produit A",
      "price": 19.99,
      "in_stock": true
    }
  ]
}
```

---

### `POST /order`

Crée une commande à partir d’un produit existant.

#### Corps attendu (JSON)

```json
{
  "product": {
    "id": 1,
    "quantity": 2
  }
}
```

#### Réponse

- **302 Redirect** vers `/order/<id>` si tout est correct.
- **422** en cas d'erreur (produit manquant, quantité invalide, produit non en stock...).

---

### `GET /order/<id>`

Récupère les détails d'une commande.

#### Réponse

```json
{
  "order": {
    "id": 12,
    "product": {
      "id": 1,
      "quantity": 2
    },
    "email": "client@mail.com",
    "shipping_information": {
      "country": "France",
      "address": "123 rue Exemple",
      "postal_code": "75000",
      "city": "Paris",
      "province": "Île-de-France"
    },
    "credit_card": {
      "name": "John Doe",
      "first_digits": "1234",
      "last_digits": "5678",
      "expiration_year": 2026,
      "expiration_month": 5
    }
  }
}
```

---

## Tests

Les tests se trouvent dans le dossier `tests/`.

Lancer les tests avec :

```bash
pytest
```

---

# Structure du projet

```
1_Projet_API/
│
├── app/
│   ├── routes.py         # Définition des routes
│   ├── models.py         # Modèles de données (Product, Order)
│   └── utils.py          # Fonctions utilitaires (calculs)
│
├── tests/                # Tests unitaires
├── .venv/                # Environnement virtuel
└── README.md             # Ce fichier
```

---

# Auteurs

- Projet API réalisé en Python/Flask dans le cadre d’un exercice de développement web fait par :
	- Makdoud Yanis
	- Bassily Enzo
	- Svezia Matéo
