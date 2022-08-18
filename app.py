from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager,  jwt_required, create_access_token, create_refresh_token
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/planets'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "super-secret"
# Mailtrap config
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '172e339bc6510c'
app.config['MAIL_PASSWORD'] = '1d6354515d34e7'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("Database created.")


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print("Database dropped.")


@app.cli.command('db_seed')
def db_seed():
    mecury = Planet(planet_name="Mecury",
                planet_type="Class D",
                home_star="Sol",
                mass=3.258e23,
                radius=1516,
                distance="35.98e6")
    
    venus = Planet(planet_name="Venus",
                planet_type="Class K",
                home_star="Sol",
                mass=4.867e24,
                radius=3760,
                distance="67.24e6")
    
    earth = Planet(planet_name="Earth",
                planet_type="Class M",
                home_star="Sol",
                mass=5.972e24,
                radius=3959,
                distance="92.96e6")

    db.session.add(mecury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name="William",
                    last_name="Herschel",
                    email="test@example.com",
                    password="password")

    db.session.add(test_user)
    db.session.commit()
    print("Database seeded.")


# Planets routes
@app.route('/planets', methods=['GET', 'POST'])
@jwt_required(optional=False)
def planets():
    if request.method == 'GET':
        planets = Planet.query.all()
        result = planets_schema.dump(planets)
        return jsonify({
            "success": True,
            "planets": result
        })
    elif request.method == 'POST':
        error = False
        planet = Planet.query.filter(Planet.planet_name==request.get_json()['planet_name']).first()
        if planet is None:
            try:
                new_planet = Planet(
                    planet_name = request.get_json()['planet_name'],
                    planet_type = request.get_json()['planet_type'],
                    home_star = request.get_json()['home_star'],
                    mass = request.get_json()['mass'],
                    radius = request.get_json()['radius'],
                    distance = request.get_json()['distance']
                )
                db.session.add(new_planet)
                db.session.commit()
            except:
                db.session.rollback()
                error = True
            finally:
                db.session.close()
            if error:
                return jsonify({
                    "success": False
                }), 500
            return jsonify({
                "success": True,
            }), 201
        return jsonify({
            "success": False,
            "message": "Planet already exists."
        }), 409


@app.route('/planets/<int:planet_id>', methods=['GET'])
def show_planet(planet_id):
    planet = Planet.query.filter(Planet.planet_id==planet_id).first()
    if planet:
        return jsonify({
            "success": True,
            "planet": planet_schema.dump(planet)
        })
    return jsonify({
        "success": False
    }), 404


@app.route('/planets/<int:planet_id>', methods=['POST'])
def update_planet(planet_id):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        error = False
        try:
            planet.planet_name = request.get_json()['planet_name']
            planet.planet_type = request.get_json()['planet_type']
            planet.home_star = request.get_json()['home_star']
            planet.mass = request.get_json()['mass']
            planet.radius = request.get_json()['radius']
            planet.distance = request.get_json()['distance']    
            db.session.commit()
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()
        if error:
            return jsonify({
                "success": False,
                "message": "An error occured"
            })
        return jsonify({
            "success": True,
            "planet": planet_schema.dump(planet)
        }), 202
    else:
        return jsonify({
            "success": False,
            "message": "Planet does not exist"
        })
        

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.filter_by(planet_id=planet_id)
    if planet:
        planet.delete()
        db.session.commit()
        return jsonify({
            "success": True,
        })
    return jsonify({
        "success": False,
        "message": "Planet not found"
    })


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    user = User.query.filter(User.email == email).first()
    if user:
        return jsonify ({
            "success": False,
            "message": "Email already exists."
        }), 409
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    password = request.form['password']
    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "success": True,
        "user": user_schema.dump(new_user)
    }), 201


# JWT
@app.route("/login", methods=['POST'])
def login():
    if request.is_json:
        email = request.get_json()['email']
        password = request.get_json()['password']
    else:
        email = request.form['email']
        password = request.form['password']

    user = User.query.filter(User.email==email, User.password==password).first()
    if user:
        access_token = create_access_token(identity=email)
        return jsonify({
            "success": True,
            "access_token": access_token
        })
    return jsonify({
        "success": False,
        "message": "Email or password incorrect."
    }), 401


@app.route('/refresh', methods=['POST'])
def refresh():
    if request.is_json:
        email = request.get_json()['email']
        password = request.get_json()['password']
    else:
        email = request.form['email']
        password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user:
        refresh_token = create_refresh_token(identity=email)
        return jsonify({
            "success": True,
            "refresh_token": refresh_token
        })
    return jsonify({
        "success": False,
        "message": "Email or password incorrect"
    })


@app.route('/retrieve-password/<string:email>', methods=['GET'])
def retrieve_password(email: String):
    user = User.query.filter(User.email==email).first()
    if user:
        msg = Message(f"Your planetary api password is: {user.password}", sender="admin@planetary-api.com", recipients=['emaikwuoloche@gmail.com'])
        mail.send(msg)
        return jsonify({
            "success": True,
            "message": f"Password sent to {email}"
        })
    return jsonify({"success": False, "message": "Email does not exist."}), 401


# Database models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String())
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == "__main__":
    app.run(debug=True)
