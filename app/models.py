from peewee import (
    Model, PostgresqlDatabase,
    CharField, IntegerField, FloatField, BooleanField, ForeignKeyField, AutoField, Select
)
import os

# Connexion à PostgreSQL avec les variables d’environnement
db = PostgresqlDatabase(
    os.getenv("DB_NAME", "api8inf349"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5432)),
)

class BaseModel(Model):
    class Meta:
        database = db

class Product(BaseModel):
    # --- HINT OPTIONNEL MAIS RECOMMANDÉ ---
    id: AutoField

    name = CharField()
    price = FloatField()
    weight = FloatField()
    in_stock = BooleanField(default=True)

class Order(BaseModel):
    # --- CORRECTION : Ajoutez ces deux lignes de type hints ---
    id: AutoField  # Indique à l'éditeur que le champ 'id' existe et quel est son type
    order_products: Select  # Indique que 'order_products' est une requête Peewee

    # Le reste de vos champs ne change pas
    email = CharField(null=True)
    shipping_country = CharField(null=True)
    shipping_address = CharField(null=True)
    shipping_postal_code = CharField(null=True)
    shipping_city = CharField(null=True)
    shipping_province = CharField(null=True)
    credit_card_name = CharField(null=True)
    credit_card_first = CharField(null=True)
    credit_card_last = CharField(null=True)
    credit_card_exp_year = IntegerField(null=True)
    credit_card_exp_month = IntegerField(null=True)
    transaction_id = CharField(null=True)
    transaction_success = BooleanField(null=True)
    transaction_amount = FloatField(null=True)
    paid = BooleanField(default=False)
    being_paid = BooleanField(default=False)

class OrderProduct(BaseModel):
    # --- HINT OPTIONNEL MAIS RECOMMANDÉ ---
    id: AutoField

    order = ForeignKeyField(Order, backref="order_products")
    product = ForeignKeyField(Product, backref="product_orders")
    quantity = IntegerField()

# Utilisé dans inf349.py pour créer les tables
models = {
    'Product': Product,
    'Order': Order,
    'OrderProduct': OrderProduct
}
