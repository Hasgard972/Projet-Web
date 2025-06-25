import requests
from .models import Product

# Taux de taxes par province
TAXES = {
    "QC": 0.15,
    "ON": 0.13,
    "AB": 0.05,
    "BC": 0.12,
    "NS": 0.14,
}

# Récupère les produits depuis l'URL distante (si l'API est en ligne)
def fetch_and_store_products():
    url = "http://dimensweb.uqac.ca/~jgnault/shops/products/"
    response = requests.get(url)
    response.raise_for_status()
    products = response.json()["products"]
    Product.delete().execute()
    for p in products:
        Product.create(**p)

# Calcul du coût de livraison
def calculate_shipping(weight):
    if weight < 500:
        return 5
    elif weight < 2000:
        return 10
    else:
        return 25

# Calcul de la taxe sur le prix total selon la province
def calculate_tax(total_price, province):
    if not province or province not in TAXES:
        return 0
    tax = TAXES[province]
    return round(total_price * (1 + tax), 2)
