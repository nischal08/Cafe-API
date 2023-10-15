import os

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# with app.app_context():
#     db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe={
        # Omit the id from the response
        # "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,

        # Put some properties in a sub-category
        "amenities": {
            "seats": random_cafe.seats,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "has_sockets": random_cafe.has_sockets,
            "can_take_calls": random_cafe.can_take_calls,
            "coffee_price": random_cafe.coffee_price,
        }
    })


@app.route("/all")
def get_all_cafe():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search")
def search():
    location = request.args["loc"]
    cafes = db.session.query(Cafe).filter(Cafe.location == location)
    print(cafes.count())
    if cafes.count() < 1:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})
    else:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes])


## HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def add():
    print(request.get_json())
    if request.method == "POST":
        name = request.get_json()['name']
        map_url = request.get_json()['map_url']
        img_url = request.get_json()['img_url']
        location = request.get_json()['location']
        seats = request.get_json()['seats']
        has_toilet = request.get_json()['has_toilet']
        has_wifi = request.get_json()['has_wifi']
        has_sockets = request.get_json()['has_sockets']
        can_take_calls = request.get_json()['can_take_calls']
        coffee_price = request.get_json()['coffee_price']
        new_cafe = Cafe(map_url=map_url, name=name, img_url=img_url, location=location, seats=seats,
                        has_toilet=has_toilet, has_wifi=has_wifi, has_sockets=has_sockets,
                        can_take_calls=can_take_calls, coffee_price=coffee_price)
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    price = request.args["new_price"]
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update is not None:
        cafe_to_update.coffee_price = price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."})


## HTTP DELETE - Delete Record
@app.route("/report_closed/<int:cafe_id>", methods=["DELETE"])
def report_closed(cafe_id):
    stored_api_key = os.environ.get('API-KEY')
    api_key = request.args["api-key"]
    if stored_api_key == api_key:
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete is not None:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully closed the cafe."})
        else:
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."})
    else:
        return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key.")


if __name__ == '__main__':
    app.run(debug=True)
