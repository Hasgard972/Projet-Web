# Objectifs
Modification suivis de commande.
Je souhaite pouvoir modifier séparement les informations suivantes de ma commande.
Quand je rentre dans ma commande sur la page web, je souhaite pouvoir
- Modifier dépendament les informations d'expédition et la paiement avec la carte bancaire.
- Je ne dois pas pouvoir faire les deux en même temps


Modifie routes.py pour satisfaire ma demande
Modifie view_order.html pour correspondre aux modifications apportés dans routes.py

# Fichiers
`````python
#routes.py
# routes.py

# ==============================================================================
# IMPORTS
# ==============================================================================
from flask import (
    Blueprint, request, jsonify, redirect, url_for, render_template,
    abort, flash, current_app
)
from peewee import DoesNotExist
from rq import Queue
from redis import Redis

from app.models import db, Product, Order, OrderProduct
from app.tasks import process_payment

# ==============================================================================
# CONFIGURATION DU BLUEPRINT ET DE LA CONNEXION REDIS
# ==============================================================================

# Création du Blueprint pour organiser les routes
bp = Blueprint("routes", __name__)

# Initialisation de la connexion à Redis et à la file d'attente (RQ)
# Note: Dans une application plus grande, cela serait géré par l'application factory
redis_conn = Redis(host="redis", port=6379)
queue = Queue(connection=redis_conn)

# ==============================================================================
# SECTION 1: ROUTES POUR L'INTERFACE UTILISATEUR (SERVANT DES PAGES HTML)
# Ces routes sont principalement destinées à un utilisateur naviguant avec
# un navigateur web.
# ==============================================================================

@bp.route("/")
def index():
    """Affiche la page d'accueil."""
    return render_template("index.html")

@bp.route("/products", methods=["GET"])
def list_products_page():
    """Affiche la liste de tous les produits disponibles."""
    # .dicts() est efficace pour transformer les résultats en dictionnaires
    products = list(Product.select().dicts())
    return render_template("produits.html", products=products)

@bp.route("/create-order", methods=["GET"])
def create_order_page():
    """Affiche le formulaire pour créer une nouvelle commande."""
    return render_template("create_order.html")

@bp.route("/order/<int:order_id>/pay", methods=["GET"])
def pay_order_page(order_id):
    """Affiche le formulaire de paiement pour une commande spécifique."""
    try:
        order = Order.get_by_id(order_id)
    except DoesNotExist:
        abort(404) # La commande n'existe pas

    # Empêcher de payer une commande déjà payée ou en cours de paiement
    if order.paid:
        flash("Cette commande a déjà été payée.", "info")
        return redirect(url_for("routes.handle_order", order_id=order.id))
    if order.being_paid:
        flash("Le paiement de cette commande est déjà en cours de traitement.", "warning")
        return redirect(url_for("routes.handle_order", order_id=order.id))

    return render_template("pay_order.html", order=order)

@bp.route("/track-order", methods=["GET"])
def track_order_page():
    """Affiche le formulaire pour suivre une commande."""
    return render_template("track_order.html")

# ==============================================================================
# SECTION 2: ROUTES DE L'API REST (COMMUNIQUANT EN JSON)
# Ces routes forment le cœur de l'API. Elles sont conçues pour être
# consommées par des clients programmatiques (ou du JavaScript côté client).
# ==============================================================================

@bp.route("/api/order", methods=["POST"])
def create_order_api():
    """
    Crée une nouvelle commande. Gère les requêtes JSON et les soumissions de formulaire.
    """
    products_data = []

    # Déterminer la source des données (JSON ou formulaire)
    if request.is_json:
        # Format supposé: {"products": [{"id": 123, "quantity": 2}, ...]}
        products_data = request.json.get("products", [])
    else:
        product_ids = request.form.getlist("id")
        quantities = request.form.getlist("quantity")
        for pid, qty in zip(product_ids, quantities):
            if pid and qty:
                products_data.append({"id": int(pid), "quantity": int(qty)})

    if not products_data:
        return jsonify({"errors": {"code": "missing-fields", "name": "La commande doit contenir au moins un produit."}}), 400

    try:
        # Utiliser une transaction pour s'assurer que tout est créé correctement ou rien du tout.
        with db.atomic() as _:
            # 1. Valider tous les produits avant de créer la commande
            validated_products = []
            for item in products_data:
                product = Product.get_by_id(item["id"])
                if not product.in_stock:
                    raise ValueError(f"Le produit ID {product.id} n'est pas en stock.")
                if int(item["quantity"]) <= 0:
                    raise ValueError("La quantité doit être supérieure à zéro.")
                validated_products.append({"product": product, "quantity": item["quantity"]})

            # 2. Si toutes les validations passent, créer la commande
            order = Order.create()

            # 3. Lier les produits à la commande
            for vp in validated_products:
                OrderProduct.create(
                    order=order,
                    product=vp["product"],
                    quantity=vp["quantity"]
                )

    except DoesNotExist:
        return jsonify({"errors": {"code": "not-found", "name": "Un des produits demandés n'existe pas."}}), 404
    except ValueError as e:
        # Gérer les erreurs de validation (stock, quantité)
        return jsonify({"errors": {"code": "invalid-request", "name": str(e)}}), 400
    except Exception as e:
        # Gérer les autres erreurs potentielles
        current_app.logger.error(f"Erreur lors de la création de commande: {e}")
        return jsonify({"errors": {"code": "internal-error", "name": "Une erreur interne est survenue."}}), 500

    # Si la création réussit, retourner une réponse appropriée
    if request.is_json:
        # Pour une API, on retourne 201 Created avec l'URL de la nouvelle ressource
        response = {
            "id": order.id,
            "location": url_for("routes.handle_order", order_id=order.id, _external=True)
        }
        return jsonify(response), 201
    else:
        # Pour un formulaire, on redirige l'utilisateur vers la page de la commande
        flash("Commande créée avec succès !", "success")
        return redirect(url_for("routes.handle_order", order_id=order.id))


@bp.route("/order/<int:order_id>", methods=["GET", "PUT"])
def handle_order(order_id):
    """
    Gère la récupération (GET) et la mise à jour (PUT) d'une commande.
    Cette route unique pour une ressource est une pratique REST standard.
    """
    try:
        order = Order.get_by_id(order_id)
    except DoesNotExist:
        # Si la commande n'existe pas, retourner 404 pour les deux méthodes (GET/PUT).
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"error": "Order not found"}), 404
        else:
            abort(404)

    # --- GESTION DE LA MÉTHODE GET ---
    if request.method == "GET":
        # Préparer la structure de données à retourner
        order_data = _build_order_dict(order)

        # Content Negotiation: décider si on renvoie du JSON ou du HTML
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({"order": order_data})
        else:
            return render_template("view_order.html", order=order_data)

    # --- GESTION DE LA MÉTHODE PUT (POUR LE PAIEMENT) ---
    elif request.method == "PUT":
        # Valider l'état de la commande avant de procéder
        if order.paid or order.being_paid:
            return jsonify({"error": "La commande est déjà payée ou en cours de traitement"}), 409 # 409 Conflict

        data = request.get_json()
        if not data or "shipping_information" not in data or "credit_card" not in data:
            return jsonify({"error": "Les informations de livraison et de carte de crédit sont requises"}), 400

        # Mettre à jour la commande avec les nouvelles informations
        _populate_shipping_info(order, data.get("shipping_information", {}))
        _populate_credit_card_info(order, data.get("credit_card", {}))

        # Marquer la commande comme "en cours de paiement" et sauvegarder
        order.being_paid = True
        order.save()

        # Préparer et lancer la tâche de paiement en arrière-plan
        payment_payload = _prepare_payment_payload(data.get("credit_card", {}))
        queue.enqueue(process_payment, order.id, payment_payload)

        # Le cahier des charges demande 202 Accepted pour cette action
        return jsonify({"message": "Le traitement du paiement a commencé."}), 202

    else :
        # Méthode non prise en charge
        return jsonify({"error": "Méthode non prise en charge"}), 405


# ==============================================================================
# SECTION 3: FONCTIONS D'AIDE (HELPERS)
# Fonctions internes pour garder le code des routes propre et organisé.
# ==============================================================================

def _build_order_dict(order: Order) -> dict:
    """Construit un dictionnaire propre à partir d'un objet Order pour la réponse."""
    products = [
        {"id": op.product.id, "name": op.product.name, "quantity": op.quantity}
        for op in order.order_products
    ]
    return {
        "id": order.id,
        "paid": order.paid,
        "being_paid": order.being_paid,
        "email": order.email,
        "products": products,
        "shipping_information": {
            "country": order.shipping_country,
            "address": order.shipping_address,
            "postal_code": order.shipping_postal_code,
            "city": order.shipping_city,
            "province": order.shipping_province
        },
        "credit_card": {
            "name": order.credit_card_name,
            "number": f"{order.credit_card_first}******{order.credit_card_last}" if order.credit_card_first else None,
            "expiration_month": order.credit_card_exp_month,
            "expiration_year": order.credit_card_exp_year
        },
        "transaction": {
            "id": order.transaction_id,
            "success": order.transaction_success,
            "amount_charged": order.transaction_amount
        } if order.transaction_id else {}
    }


def _populate_shipping_info(order: Order, shipping_data: dict):
    """Met à jour l'objet Order avec les informations de livraison."""
    order.email = shipping_data.get("email")
    order.shipping_country = shipping_data.get("country")
    order.shipping_address = shipping_data.get("address")
    order.shipping_postal_code = shipping_data.get("postal_code")
    order.shipping_city = shipping_data.get("city")
    order.shipping_province = shipping_data.get("province")


def _populate_credit_card_info(order: Order, credit_card_data: dict):
    """Met à jour l'objet Order avec les informations non sensibles de la carte."""
    card_number = credit_card_data.get("number", "")
    order.credit_card_name = credit_card_data.get("name")
    order.credit_card_first = card_number[:4] # Le spec dit "first_digits" (souvent 4)
    order.credit_card_last = card_number[-4:]
    order.credit_card_exp_month = int(credit_card_data.get("expiration_month", 0))
    order.credit_card_exp_year = int(credit_card_data.get("expiration_year", 0))


def _prepare_payment_payload(credit_card_data: dict) -> dict:
    """Crée le dictionnaire avec les données sensibles de la carte pour le processeur de paiement."""
    return {
        "name": credit_card_data.get("name"),
        "number": credit_card_data.get("number"),
        "expiration_month": credit_card_data.get("expiration_month"),
        "expiration_year": credit_card_data.get("expiration_year"),
        "cvv": credit_card_data.get("cvv")
    }
`````

````html
# view_order.html

<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Commande #{{ order.id }}</title>
</head>
<body>
    <h1>Commande #{{ order.id }}</h1>

    {% if order.products %}
    <h2>Produits</h2>
    <ul>
        {% for p in order.products %}
        <li>{{ p.name }} (ID {{ p.id }}) - Quantité : {{ p.quantity }}</li>
        {% endfor %}
    </ul>
    {% else %}
    <p>Aucun produit trouvé dans cette commande.</p>
    {% endif %}

    <h2>Client</h2>
    <p>Email : {{ order.email or 'Non fourni' }}</p>

    <h3>Adresse de livraison</h3>
    <p>{{ order.shipping_information.address }}, {{ order.shipping_information.postal_code }} {{ order.shipping_information.city }}, {{ order.shipping_information.province }}, {{ order.shipping_information.country }}</p>

    <h3>Carte</h3>
    <p>Nom : {{ order.credit_card.name }}</p>
    <p>Numéro : {{ order.credit_card.number }}</p>
    <p>Expiration : {{ order.credit_card.expiration_month }}/{{ order.credit_card.expiration_year }}</p>

    <h3>Transaction</h3>
    {% if order.transaction %}
        <p>ID : {{ order.transaction.id }}</p>
        <p>Succès : {{ "Oui" if order.transaction.success else "Non" }}</p>
        <p>Montant : {{ order.transaction.amount_charged }} €</p>
    {% else %}
        <p>Aucune transaction enregistrée.</p>
    {% endif %}

    <h3>Statut</h3>
    <p><strong>{{ "✅ Payée" if order.paid else "🕒 En attente" }}</strong></p>

    <p><a href="/">Retour à l'accueil</a></p>
</body>
</html>

````