from datetime import datetime
import os
# this is the patient routes which will be used to handle the patient related routes
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from extensions import db
from tasks.send_email import send_email, send_reminder_email
from tasks.patient_treatment_export import export_patient_treatments
from tasks.patient_appointment_export import export_patient_appointments
from utils.cache import get_cache, set_cache
from models import Patient, Doctor, Appointment, Treatment, Department, User

patient_bp = Blueprint("patient", __name__, url_prefix="/api/patient")
# making commnet to push code in github


# check patient role 
#this function checks whether the logged-in user has the role patient
def patient_only():
    claims = get_jwt()  # Claims = token ke andar stored information
    return claims.get("role") == "patient"


# get patient by token 
def get_patient_by_token():
    user_id = int(get_jwt_identity())  # get_jwt_identity ,Ye JWT token se user ID nikalta hai.
    return Patient.query.filter_by(user_id=user_id).first()  # Patient table me jo record us user_id(mtlb jo hmne get_jwt_identity se nikali) se linked hai, wo return karta hai



@patient_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_my_profile():
    if not patient_only():
        return jsonify({"error": "Patient can access only"}), 403

    patient = get_patient_by_token()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    user = User.query.get(patient.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user.username,
        "full_name": patient.full_name,
        "age": patient.age,
        "contact": patient.contact
    }), 200


@patient_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_my_profile():
    if not patient_only():
        return jsonify({"error": "Patient can access only"}), 403

    patient = get_patient_by_token()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    user = User.query.get(patient.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}

    if "username" in data:
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
        contact = data.get("contact")
        patient.contact = contact.strip() if isinstance(contact, str) else contact

    db.session.commit()
    return jsonify({
        "message": "Profile updated successfully",
        "profile": {
            "username": user.username,
            "full_name": patient.full_name,
            "age": patient.age,
            "contact": patient.contact
        }
    }), 200


#this get aip allows a patient to view the list of hospital departments but authenticated patients only.
@patient_bp.route("/departments", methods=["GET"])
@jwt_required() # Only logged-in user access kr skta h
def view_departments():
    if not patient_only():
        return jsonify({"error": "Patient can access only"}), 403

    cached = get_cache("departments_list")
    if cached:  # First we check if data is already stored in cache (Redis). If yes, we return it directly without hitting the database
        return jsonify(cached)

    departments = Department.query.all()  # fatch departments from db
    result = [
        {"id": d.id, "name": d.name, "description": d.description}
        for d in departments
    ]   # covert data to json format

    set_cache("departments_list", result)  #we store response in cache so next request fast ho jaye
    return jsonify(result), 200


# doctore view krne ka route by specialization
@patient_bp.route("/doctors", methods=["GET"])
@jwt_required()
def get_doctors():
    specialization = request.args.get("specialization")

    doctors = (
        db.session.query(Doctor, User)
        .join(User, Doctor.user_id == User.id)
        .filter(Doctor.specialization == specialization)
        .all()
    )

    return jsonify([
        {
            "id": d.id,
            "name": u.username,
            "specialization": d.specialization,
            "availability": d.availability or {}
        }
        for d, u in doctors
    ]), 200


# book appoitement wala route from here i will control all booking wala syatem




@patient_bp.route("/appointments", methods=["POST"])
@jwt_required()
def book_appointment():
    if not patient_only():
        return jsonify({"error": "Patient can access only"}), 403

    patient = get_patient_by_token()
    data = request.get_json()

    doctor_id_from_frontend = data.get("doctor_id")
    date_str = data.get("date")
    time_str = data.get("time")

    if not all([doctor_id_from_frontend, date_str, time_str]):
        return jsonify({"error": "Missing required fields"}), 400

    # Ensure integer ID
    try:
        doctor_id_from_frontend = int(doctor_id_from_frontend)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid doctor id"}), 400

    # Frontend sends Doctor.id, so fetch by Doctor.id only
    # Using OR with Doctor.user_id can match the wrong doctor if IDs overlap.
    doctor = Doctor.query.filter(Doctor.id == doctor_id_from_frontend).first()

    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    # Convert date + time → datetime
    try:
        appointment_dt = datetime.fromisoformat(f"{date_str} {time_str}")
    except ValueError:
        return jsonify({"error": "Invalid date/time format"}), 400

    # Check if slot already booked
    exists = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_time == appointment_dt
    ).first()

    if exists:
        return jsonify({"error": "Slot already booked"}), 409

    # Save appointment with correct doctor.id
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_time=appointment_dt,
        status="Booked"
    )

    db.session.add(appointment)
    db.session.commit()

    # emial part 
    try:
        patient_user = User.query.get(patient.user_id)
        doctor_user = User.query.get(doctor.user_id)

        recipients = ["anshusharma3540@gmail.com"]
        if patient_user.email and "@" in patient_user.email:
            recipients.append(patient_user.email)

        send_email.delay(
            subject="New Appointment Booked",
            recipients=recipients,
            body=f"""
New Appointment Details

Patient: {patient_user.username}
Doctor: {doctor_user.username}
Date: {date_str}
Time: {time_str}
"""
        )

        send_reminder_email.apply_async(
            args=(
                "Appointment Reminder",
                recipients,
                f"Reminder: Appointment with Dr. {doctor_user.username} at {time_str} on {date_str}"
            ),
            countdown=120
        )

    except Exception as e:
        print("EMAIL ERROR:", e)

    return jsonify({"message": "Appointment booked successfully"}), 201

# view my appointments route
@patient_bp.route("/appointments", methods=["GET"])
@jwt_required()
def my_appointments():
    if not patient_only():
        return jsonify({"error": "Patient can access only"}), 403

    patient = get_patient_by_token()
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()

    return jsonify([
        {
            "appointment_id": a.id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "date": a.appointment_time.date().isoformat(),
            "time": a.appointment_time.strftime("%H:%M"),
            "status": a.status
        }
        for a in appointments
    ]), 200

# view treatment history route of logged in patient 
@patient_bp.route("/treatments", methods=["GET"])
@jwt_required()
def treatment_history():
    if not patient_only():
        return jsonify({"error": "Patient can access only"}), 403

    patient = get_patient_by_token() # token se current patient ka database record fetch karte hain

    treatments = (
        db.session.query(Treatment, Appointment, Doctor)
        .join(Appointment, Treatment.appointment_id == Appointment.id)  #treatment table ko appointment se joda
        .join(Doctor, Appointment.doctor_id == Doctor.id) #appointment ko doctor se joda,
        .filter(Appointment.patient_id == patient.id) # then onley us patient ke records liye jo login hai
        .all()
    )

    return jsonify([
        {
            "diagnosis": t.diagnosis,
            "prescription": t.prescription,
            "notes": t.notes,
            "doctor_name": d.full_name,
            "date": a.appointment_time.date().isoformat(),
            "time": a.appointment_time.strftime("%H:%M")
        }
        for t, a, d in treatments
    ]), 200


# export patient data to csv route

@patient_bp.route("/export-csv", methods=["POST"])
@jwt_required()
def export_csv():
    patient = get_patient_by_token()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXPORT_FOLDER = os.path.join(BASE_DIR, "..", "exports")
    os.makedirs(EXPORT_FOLDER, exist_ok=True)

    treatment_file = os.path.join(EXPORT_FOLDER, f"patient_{patient.id}_treatments.csv")
    appointment_file = os.path.join(EXPORT_FOLDER, f"patient_{patient.id}_appointments.csv")

    for file_path in (treatment_file, appointment_file):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                # If cleanup fails, proceed; download will still work if new file is generated.
                pass

    # Check if treatment exists via appointment link
    has_treatment = (
        Treatment.query
        .join(Appointment)
        .filter(Appointment.patient_id == patient.id)
        .first()
    )

    if has_treatment:
        export_patient_treatments.delay(patient.id)
    else:
        export_patient_appointments.delay(patient.id)

    return {"message": "Export started"}, 202

# this api allows a logged-in patient to download their medical data in csv format basically hamara csv export wla system
@patient_bp.route("/download-csv", methods=["GET"])
@jwt_required()
def download_csv():
    if not patient_only():
        return jsonify({"error": "Patient can access only"}), 403

    patient = get_patient_by_token()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # routes folder
    EXPORT_FOLDER = os.path.join(BASE_DIR, "..", "exports")
     # We create a patient-specific file path using f-string and os.path.join
    treatment_file = os.path.join(EXPORT_FOLDER, f"patient_{patient.id}_treatments.csv")
    appointment_file = os.path.join(EXPORT_FOLDER, f"patient_{patient.id}_appointments.csv")

    # Check treatment file first
    if os.path.exists(treatment_file):
        return send_file(
            treatment_file,
            as_attachment=True,  # File browser me open nahi hogi, direct download hogi agr flase then text will be open in browser
            download_name="treatments.csv",
            mimetype="text/csv"
        )

    # Then appointment file
    if os.path.exists(appointment_file):
        return send_file(
            appointment_file,
            as_attachment=True,
            download_name="appointments.csv",
            mimetype="text/csv"
        )

    has_treatment = (
        Treatment.query
        .join(Appointment)
        .filter(Appointment.patient_id == patient.id)
        .first()
    )

    if has_treatment:
        export_patient_treatments.delay(patient.id)
    else:
        export_patient_appointments.delay(patient.id)

    return jsonify({"message": "CSV is being generated. Please try again in a few seconds."}), 202

# “CSV files are usually generated by background tasks (like Celery jobs), and this API just serves the file once ready
