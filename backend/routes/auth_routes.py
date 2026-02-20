from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from extensions import db

from models import User, Patient


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# this is the rajister route for patient onley  paitent can rajister itself
@auth_bp.route("/register", methods=["POST"])
def register_patient():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")
    age = data.get("age")
    contact = data.get("contact")

    if not username or not password or not full_name:
        return jsonify({"error": "required fields missing"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "user already exists"}), 409

    user = User(username=username, role="patient")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    patient = Patient(
        user_id=user.id,
        full_name=full_name,
        age=age,
        contact=contact
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({"message": "patient registered successfuly"}), 201


#  login route for all users
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "user name and pass missing"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "invalid inputs"}), 401

    if not user.active:
        return jsonify({"error": "user blocked"}), 403

    
    access_token = create_access_token(
        identity=str(user.id),                
        additional_claims={"role": user.role}  
    )

    return jsonify({
        "access_token": access_token,
        "role": user.role
    }), 200
