# tasks.py
from app.models import Order, OrderProduct, db
from app.utils import calculate_shipping, calculate_tax
from time import sleep
import random
import requests  # Pour simuler l'appel externe


def process_payment(order_id, credit_card):
    """Traitement du paiement en tâche de fond."""
    print(f"🔄 Paiement en cours pour la commande #{order_id}")

    # Assurer la connexion à la BDD dans le worker
    if db.is_closed():
        db.connect()

    order = Order.get_by_id(order_id)

    # 1. Calculer le prix total des produits et le poids total
    total_product_price = 0
    total_weight = 0
    for op in order.order_products:
        total_product_price += op.product.price * op.quantity
        total_weight += op.product.weight * op.quantity

    # 2. Calculer le coût de livraison
    shipping_price = calculate_shipping(total_weight)

    # 3. Calculer le prix total AVEC taxes (basé sur le prix des produits + livraison)
    # Le cahier des charges est ambigu, mais taxer la livraison est courant.
    # Assumons que la taxe s'applique sur le sous-total (produits + livraison).
    sub_total = total_product_price + shipping_price
    total_price_with_tax = calculate_tax(sub_total, order.shipping_province)

    # Simuler l'appel à l'API de paiement externe
    # url = "http://dimensweb.uqac.ca/~jgnault/shops/pay/"
    # payload = { "credit_card": credit_card, "amount_charged": total_price_with_tax }
    # response = requests.post(url, json=payload)

    # Pour la simulation locale :
    sleep(3)
    success = random.choice([True, True, True, False])  # 75% de réussite

    # Mise à jour de la commande
    order.credit_card_name = credit_card.get("name")
    order.credit_card_first = credit_card.get("number", "")[:4]  # Le spec dit "first_digits"
    order.credit_card_last = credit_card.get("number", "")[-4:]
    order.credit_card_exp_month = int(credit_card.get("expiration_month", 0))
    order.credit_card_exp_year = int(credit_card.get("expiration_year", 0))

    order.transaction_id = str(random.randint(1000000000, 9999999999))
    order.transaction_success = success
    order.transaction_amount = total_price_with_tax  # Utiliser le montant correct
    order.paid = success
    order.being_paid = False
    order.save()

    if success:
        print(f"✅ Paiement réussi pour la commande #{order.id}")
    else:
        print(f"❌ Paiement refusé pour la commande #{order.id}")

    if not db.is_closed():
        db.close()