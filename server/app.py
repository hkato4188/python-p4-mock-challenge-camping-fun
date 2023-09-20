#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return 'We are home!'

@app.route('/activities')
def activities():
    all_activities = [a.to_dict() for a in Activity.query.all()]
    return make_response(all_activities, 200)
    
@app.route('/activities/<int:id>', methods=["DELETE"])
def activity(id):
    activity = Activity.query.filter(Activity.id == id).first()
    if activity:
        for s in activity.signups:
            db.session.delete(s)
        db.session.delete(activity)
        db.session.commit()
        return make_response({}, 204)
    else:
        return make_response({"error": "Activity not found"}, 404)        


@app.route('/campers', methods=["GET", "POST"])
def campers():
    if request.method == "GET":
        all_campers = [c.to_dict() for c in Camper.query.all()]
        return make_response(all_campers, 200)
    elif request.method == "POST":
        try:
            data = request.get_json()
            camper = Camper(
                name = data['name'],
                age = data['age']
            )
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(), 201)
        except:
            return make_response({"errors": ["validation errors"]},400)
            # error is 422

@app.route('/campers/<int:id>', methods=["GET", "PATCH"])
def camper(id):
    camper = Camper.query.filter(Camper.id == id).first()
    if camper:
        if request.method == "GET":
            return make_response(camper.to_dict_su_act(), 200)
        elif request.method == "PATCH":
            try:
                data = request.get_json()
                for key in data:
                    setattr(camper, key, data[key])
                db.session.add(camper)
                db.session.commit()
                return make_response(camper.to_dict(), 202)
            except:
                return make_response({"errors": ["validation errors"]},400)
                # error is 422
    else:
        return make_response({"error": "Camper not found"}, 404)


@app.route('/signups', methods=["GET", "POST"])
def signups():
    if request.method == "GET":
        all_signups = [s.to_dict() for s in Signup.query.all()]
        return make_response(all_signups, 200)
    elif request.method == "POST":
        try:
            data = request.get_json()
            new_signup = Signup(
                camper_id = data['camper_id'],
                activity_id = data['activity_id'],
                time = data['time']
            )
            db.session.add(new_signup)
            db.session.commit()
            return make_response(new_signup.signup_to_dict_full_details(), 200)
                    # error is 201
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        # error is 422


if __name__ == '__main__':
    app.run(port=5555, debug=True)
