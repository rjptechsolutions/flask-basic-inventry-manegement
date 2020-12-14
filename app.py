from flask import Flask, request, jsonify,url_for,redirect,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init FLASK App
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Databse
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'+os.pardir.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TACK_MODIFICATION'] = False

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

#basic http authentication
@app.route("/login")
def login():
    if request.authorization and request.authorization == 'username' and request.authorization == 'password':
        return redirect(url_for('get_products'))
    return redirect(url_for('login'))


#Product Model
class Product(db):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self,name,description,price,qty):
        self.name = name
        self.description=description
        self.price=price
        self.qty=qty

# User Model
class Order(db):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))   
    address = db.Column(db.String(300))
    phone = db.Column(db.String(15))
    prod_id = db.Column(db.Integer,ForeignKey("Product.id"),nullable=False)

    def __init__(self,username,email,address,phone,prod_id):
        self.username = username
        self.email = email 
        self.address = address 
        self.phone = phone 
        self.prod_id = prod_id

# Product Schema
class ProductSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'description', 'price', 'qty')

# Init schema
product_schema = ProductSchema(strict=True)
products_schema = ProductSchema(many=True, strict=True)

# Order Schema
class OrderSchema(ma.Schema):
  class Meta:
    fields = ('id', 'username','email','address', 'phone', 'prod_id')

# Init schema
order_schema = OrderSchema(strict=True)
orders_schema = OrderSchema(many=True, strict=True)

# Create a Order
@app.route('/order', methods=['POST'])
def update_product(id):
  product = Product.query.get(id)
  qty = product_schema.qty - 1
  product.qty = qty
  db.session.commit()

def add_order():
  username = request.json['username']
  address = request.json['address']
  email = request.json['email']
  phone = request.json['phone']
  prod_id = request.json['prod_id']  
  new_order = Order(username, address, email, phone,prod_id)

  db.session.add(new_order)
  update_product(prod_id)
  db.session.commit()

  return product_schema.jsonify(new_order)

# Get All Order
@app.route('/orders', methods=['GET'])
def get_orders():
  all_orders = Order.query.all()
  result = order_schema.dump(all_orders)
  return jsonify(result.data)

# Create a Product
@app.route('/product', methods=['POST'])
def add_product():
  name = request.json['name']
  description = request.json['description']
  price = request.json['price']
  qty = request.json['qty']

  new_product = Product(name, description, price, qty)

  db.session.add(new_product)
  db.session.commit()

  return product_schema.jsonify(new_product)

# Get All Products
@app.route('/product', methods=['GET'])
def get_products():
  all_products = Product.query.all()
  result = products_schema.dump(all_products)
  return jsonify(result.data)

# Get Single Products
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
  product = Product.query.get(id)
  return product_schema.jsonify(product)

# Update a Product
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
  product = Product.query.get(id)

  name = request.json['name']
  description = request.json['description']
  price = request.json['price']
  qty = request.json['qty']

  product.name = name
  product.description = description
  product.price = price
  product.qty = qty

  db.session.commit()

  return product_schema.jsonify(product)

# Delete Product
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
  product = Product.query.get(id)
  db.session.delete(product)
  db.session.commit()

  return product_schema.jsonify(product)


@app.route('/')
def hello():
    return jsonify({'msg':'Hello World'})


#run server
if __name__ == "__main__":
    app.run(debug=True)


