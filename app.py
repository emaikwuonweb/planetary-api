from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/planets'
db = SQLAlchemy(app)

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
    # db.session.commit()



    


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


if __name__ == "__main__":
    app.run(debug=True)
