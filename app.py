from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/planets'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

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
@app.route('/planets', methods=['GET'])
def planets():
    planets = Planet.query.all()
    result = planets_schema.dump(planets)
    return jsonify({
        "success": True,
        "planets": result
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
