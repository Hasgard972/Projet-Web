import requests

BASE_URL = "http://localhost:5000"

## Étape 1 : Créer une commande
print("📦 Création de la commande...")
res = requests.post(f"{BASE_URL}/order", json={
    "product": {
        "id": 1,
        "quantity": 1
    }
})

print(res)

if res.status_code not in (200, 302):
    print("❌ Erreur lors de la création de la commande :", res.status_code, res.text)
    exit(1)

# Extraire l'ID depuis la réponse
if res.status_code == 302:
    location = res.headers["Location"]
    order_id = location.split("/")[-1]
else:  # code 200
    order_id = str(res.json()["order"]["id"])

print(f"✅ Commande créée avec ID {order_id}")

# Étape 2 : Ajouter les infos de livraison
print("📮 Ajout des informations de livraison...")
res2 = requests.put(f"{BASE_URL}/order/{order_id}", json={
    "order": {
        "email": "mateo@example.com",
        "shipping_information": {
            "country": "Canada",
            "address": "123 Rue Principale",
            "postal_code": "G1X 2B3",
            "city": "Québec",
            "province": "QC"
        }
    }
})

if res2.status_code != 200:
    print("❌ Erreur lors de l'ajout de livraison :", res2.status_code, res2.text)
    exit(1)

print("✅ Livraison ajoutée")

# Étape 3 : Effectuer le paiement
print("💳 Paiement de la commande...")
res3 = requests.put(f"{BASE_URL}/order/{order_id}", json={
    "credit_card": {
        "name": "Jean Testeur",
        "number": "4242 4242 4242 4242",
        "expiration_year": 2025,
        "expiration_month": 12,
        "cvv": "123"
    }
})

if res3.status_code != 200:
    print("❌ Échec du paiement :", res3.status_code, res3.text)
    exit(1)

print("✅ Paiement réussi")

# Étape 4 : Afficher la commande finale
print("📄 Détails de la commande :")
res4 = requests.get(f"{BASE_URL}/order/{order_id}")
print(res4.json())
