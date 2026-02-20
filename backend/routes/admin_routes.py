from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from extensions import db
from models import User, Doctor, Patient, Appointment, Treatment

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# check admin role
def admin_only():
    claims = get_jwt()
    return claims.get("role") == "admin"


# dashboard route of admin
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if not admin_only():
        return jsonify({"error": "Admin access only"}), 403

    return jsonify({
        "total_doctors": Doctor.query.count(),
        "total_patients": Patient.query.count(),
        "total_appointments": Appointment.query.count()
    })



@admin_bp.route("/doctors", methods=["POST"])
@jwt_required()  # check ki tocken vaild or not if not retrun 401(unauthorized)
def add_doctor():
    if not admin_only():
        return jsonify({"error": "Admin access only"}), 403

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")
    specialization = data.get("specialization")
    experience_years = data.get("experience_years")

    if not username or not password or not full_name or not specialization:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    user = User(username=username, role="doctor", active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    doctor = Doctor(
        user_id=user.id,
        full_name=full_name,
        specialization=specialization,
        experience_years=experience_years
    )
    db.session.add(doctor)
    db.session.commit()

    return jsonify({"message": "Doctor added successfully"}), 201


# view all doctors route
@admin_bp.route("/doctors", methods=["GET"])
@jwt_required()
def view_doctors():
    if not admin_only():
        return jsonify({"error": "onley admin can access"}), 403

    doctors = (
        db.session.query(Doctor, User)
        .join(User, Doctor.user_id == User.id)
        .all()
    )

    return jsonify([
        {
            "id": d.id,
            "user_id": u.id,
            "name": d.full_name,
            "specialization": d.specialization,
            "experience": d.experience_years,
            "active": u.active
        }
        for d, u in doctors
    ])


# view all patients route
@admin_bp.route("/patients", methods=["GET"])
@jwt_required()
def view_patients():
    if not admin_only():
        return jsonify({"error": "onley admin can access"}), 403

    patients = (
        db.session.query(Patient, User)
        .join(User, Patient.user_id == User.id)
        .all()
    )

    return jsonify([
        {
            "id": p.id,
            "user_id": u.id,
            "username": u.username,
            "full_name": p.full_name,
            "age": p.age,
            "contact": p.contact,
            "active": u.active
        }
        for p, u in patients
    ])


# updarte doctor route here
@admin_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
@jwt_required()
def update_doctor(doctor_id):
    if not admin_only():
        return jsonify({"error": "onley admin can access"}), 403

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    user = User.query.get(doctor.user_id)
    data = request.get_json()

    if "name" in data:
        doctor.full_name = data["name"]

    if "specialization" in data:
        doctor.specialization = data["specialization"]

    if "experience" in data:
        doctor.experience_years = data["experience"]
    elif "experience_years" in data:
        doctor.experience_years = data["experience_years"]

    if "active" in data and user:
        user.active = data["active"]

    db.session.commit()
    return jsonify({"message": "Doctor updated successfully"}), 200


# toggle user active status route
@admin_bp.route("/users/<int:user_id>/toggle", methods=["PUT"])
@jwt_required()  # Only logged-in users with valid token can access this API.
def toggle_user(user_id):
    if not admin_only():  # even if logged in but not admin  then return 403 becouse bhai onley admin can delete 
        return jsonify({"error": "Admin access only"}), 403

    user = User.query.get(user_id)  # Fetch doctor from db using primary key.
    if not user:  # If record doesn’t exist, return proper error instead of crashing.”
        return jsonify({"error": "User not found"}), 404

    user.active = not user.active
    db.session.commit()

    return jsonify({
        "message": "User status updated",
        "active": user.active
    })


# view all appointments route
@admin_bp.route("/appointments", methods=["GET"])
@jwt_required()
def view_appointments():
    if not admin_only():
        return jsonify({"error": "onley admin can access"}), 403

    results = (
        db.session.query(Appointment, Patient, User, Doctor)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(User, Patient.user_id == User.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .all()
    )

    return jsonify([
        {
            "appointment_id": a.id,
            "patient_id": p.id,
            "patient_name": u.username,
            "doctor_id": d.id,
            "doctor_name": d.full_name,
            "date": a.appointment_time.date().isoformat(),
            "time": a.appointment_time.strftime("%H:%M"),

            "status": a.status
        }
        for a, p, u, d in results
    ])


# delete doctor route here
@admin_bp.route("/doctors/<int:doctor_id>", methods=["DELETE"]) # this delete api is  used to delete a doctor by admin
@jwt_required()
def delete_doctor(doctor_id):
    if not admin_only():
        return jsonify({"error": "Admin only"}), 403

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    user = User.query.get(doctor.user_id)

    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    appointment_ids = [a.id for a in appointments]
    if appointment_ids:
        Treatment.query.filter(Treatment.appointment_id.in_(appointment_ids)).delete(
            synchronize_session=False
        )
        Appointment.query.filter(Appointment.id.in_(appointment_ids)).delete(
            synchronize_session=False
        )

    db.session.delete(doctor)   # first delete doctor record from doctor table
     # then delete user record from user table yahi maintain referential integrity hota h
    if user and user.role == "doctor":
        db.session.delete(user)

    db.session.commit()  # save changes to database parmanent
    return jsonify({"message": "Doctor deleted successfully"}), 200  # return success message in proper json format


# update patient route
@admin_bp.route("/patients/<int:patient_id>", methods=["PUT"])  #URL(url parameter <int:patient_id> ) me dynamic value aayegi wo bhi integer
@jwt_required()
def update_patient(patient_id):
    if not admin_only():
        return jsonify({"error": "onley admin can access"}), 403

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    user = User.query.get(patient.user_id)
    data = request.get_json() or {}

    if "username" in data and user:
        username = (data.get("username") or "").strip()
        if not username:
            return jsonify({"error": "Username is required"}), 400

        exists = User.query.filter(
            User.username == username,
            User.id != user.id
        ).first()
        if exists:
            return jsonify({"error": "Username already exists"}), 409
        user.username = username

    if "full_name" in data:
        full_name = (data.get("full_name") or "").strip()
        if not full_name:
            return jsonify({"error": "Full name is required"}), 400
        patient.full_name = full_name

    if "age" in data:
        age = data.get("age")
        if age in ("", None):
            patient.age = None
        else:
            try:
                patient.age = int(age)
            except (TypeError, ValueError):
                return jsonify({"error": "Invalid age"}), 400

    if "contact" in data:
        patient.contact = data.get("contact")

    if "active" in data and user:
        user.active = bool(data["active"])

    db.session.commit()
    return jsonify({"message": "Patient updated successfully"}), 200


# delete patient route
@admin_bp.route("/patients/<int:patient_id>", methods=["DELETE"])
@jwt_required()
def delete_patient(patient_id):
    if not admin_only():
        return jsonify({"error": "Admin only"}), 403

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    user = User.query.get(patient.user_id)

    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    appointment_ids = [a.id for a in appointments]
    if appointment_ids:
        Treatment.query.filter(Treatment.appointment_id.in_(appointment_ids)).delete(
            synchronize_session=False
        )
        Appointment.query.filter(Appointment.id.in_(appointment_ids)).delete(
            synchronize_session=False
        )

    db.session.delete(patient)
    if user and user.role == "patient":
        db.session.delete(user)

    db.session.commit()
    return jsonify({"message": "Patient deleted successfully"}), 200


# view the patient history route
@admin_bp.route("/patients/<int:patient_id>/history", methods=["GET"])
@jwt_required()
def admin_patient_history(patient_id):
    if not admin_only():
        return jsonify({"error": "onley admin can access"}), 403

    patient = (
        db.session.query(Patient, User)
        .join(User, Patient.user_id == User.id)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    treatments = (
        db.session.query(Treatment)
        .join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(Appointment.patient_id == patient_id)
        .all()
    )

    return jsonify({
        "patient_name": patient[1].username,
        "history": [
            {
                "diagnosis": t.diagnosis,
                "prescription": t.prescription,
                "notes": t.notes
            } for t in treatments
        ]
    })
