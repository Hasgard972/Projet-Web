from flask import Blueprint, render_template
from .models import Product
from .routes import get_order

bp = Blueprint("html", __name__, url_prefix="/html")

@bp.route("/products")
def html_products():
    products = [p.__data__ for p in Product.select()]
    return render_template("index.html", products=products)

@bp.route("/create")
def html_create():
    return render_template("create_order.html")

@bp.route("/order/<int:order_id>")
def html_view_order(order_id):
    response, status = get_order(order_id)
    if status == 200:
        return render_template("view_order.html", order=response.get_json())
    return f"Commande {order_id} introuvable", status

@bp.route("/pay")
def html_pay():
    return render_template("pay_order.html")
