from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from datetime import date, datetime
import csv
import os
# this is the doctor routes which will be used to handle the doctor related routes
# add commnt to push the code on gitub
from extensions import db
from models import Doctor, Appointment, Treatment, Patient, User

doctor_bp = Blueprint("doctor", __name__, url_prefix="/api/doctor")


# this is for checking the role of doctor because only doctor can access these routes
def doctor_only():
    claims = get_jwt()
    return claims.get("role") == "doctor"


def get_doctor_by_token():
    user_id = int(get_jwt_identity())
    return Doctor.query.filter_by(user_id=user_id).first()


# doctore will provide the ablity through this route 
@doctor_bp.route("/availability", methods=["POST"])
@jwt_required()
def set_availability():
    if not doctor_only():
        return jsonify({"error": "only doctor can access"}), 403

    doctor = get_doctor_by_token()
    if not doctor:
        return jsonify({"error": "doctor not found"}), 404

    data = request.get_json()
    expanded = {}

    for d, ranges in data.items():
        slots = []
        for r in ranges:
            try:
                start, end = r.split("-")
                sh, eh = int(start[:2]), int(end[:2])
                for h in range(sh, eh):
                    slots.append(f"{h:02d}:00")
            except:
                continue
        if slots:
            expanded[d] = slots

    doctor.availability = expanded
    db.session.commit()
    return jsonify({"message": "availability updated"}), 200


# this route is for doctore apoitemnets ko dekhne ke liye 
@doctor_bp.route("/appointments", methods=["GET"])
@jwt_required()
def my_appointments():
    user_id = int(get_jwt_identity())

    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    results = (
        db.session.query(Appointment, Patient, User)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(User, Patient.user_id == User.id)
        .filter(Appointment.doctor_id == doctor.id)
        .all()
    )

    return jsonify([
        {
            "appointment_id": a.id,
            "patient_id": p.id,
            "patient_name": u.username,
            "date": a.appointment_time.date().isoformat(),
            "time": a.appointment_time.strftime("%H:%M"),
            "status": a.status
        }
        for a, p, u in results
    ])


# this is for update status of paitent
@doctor_bp.route("/appointments/<int:appointment_id>/status", methods=["PUT"])
@jwt_required()
def update_status(appointment_id):
    if not doctor_only():
        return jsonify({"error": "only doctor can access"}), 403

    status = request.get_json().get("status")
    if status not in ["Completed", "Cancelled"]:
        return jsonify({"error": "Invalid status"}), 400

    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = status
    db.session.commit()
    return jsonify({"message": "status updated"}), 200


# this route is for add treatment appoitemnt
@doctor_bp.route("/appointments/<int:appointment_id>/treatment", methods=["POST"])
@jwt_required()
def add_treatment(appointment_id):
    if not doctor_only():
        return jsonify({"error": "only doctor can access"}), 403

    data = request.get_json()
    appointment = Appointment.query.get_or_404(appointment_id)

    treatment = Treatment(
        appointment_id=appointment.id,
        diagnosis=data.get("diagnosis"),
        prescription=data.get("prescription"),
        notes=data.get("notes")
    )

    db.session.add(treatment)
    appointment.status = "Completed"
    db.session.commit()
    return jsonify({"message": "treatment added"}), 201


# route for monthly report of doctor appoitemnts
@doctor_bp.route("/monthly-report", methods=["GET"])
@jwt_required()
def monthly_report():
    if not doctor_only():
        return jsonify({"error": "only doctor can access"}), 403

    doctor = get_doctor_by_token()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    today = datetime.utcnow()
    year = request.args.get("year", type=int) or today.year
    month = request.args.get("month", type=int) or today.month

    if month < 1 or month > 12:
        return jsonify({"error": "Invalid month"}), 400

    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    report_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(report_dir, exist_ok=True)
    filename = f"doctor_{doctor.id}_monthly_{year}_{month:02d}.csv"
    file_path = os.path.join(report_dir, filename)

    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_time >= start,
        Appointment.appointment_time < end
    ).all()
    completed_count = sum(1 for a in appointments if a.status == "Completed")

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Doctor ID", "Doctor Name", "Month", "Year", "Completed Appointments"])
        writer.writerow([doctor.id, doctor.full_name, f"{month:02d}", year, completed_count])
        writer.writerow([])
        writer.writerow(["Appointment ID", "Patient ID", "Date", "Time", "Status"])
        for a in appointments:
            writer.writerow([
                a.id,
                a.patient_id,
                a.appointment_time.date().isoformat(),
                a.appointment_time.strftime("%H:%M"),
                a.status
            ])

    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype="text/csv"
    )

    return jsonify({"message": "treatment added"}), 201


# this route is for doctor to see the history of paitent
@doctor_bp.route("/patients/<int:patient_id>/history", methods=["GET"])
@jwt_required()
def patient_history(patient_id):
    if not doctor_only():
        return jsonify({"error": "Doctor access only"}), 403
    
    doctor = get_doctor_by_token()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    treatments = (
        db.session.query(Treatment)
        .join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(
            Appointment.patient_id == patient_id,
            Appointment.doctor_id == doctor.id
        )
        .all()
    )

    return jsonify([
        {
            "diagnosis": t.diagnosis,
            "prescription": t.prescription,
            "notes": t.notes
        }
        for t in treatments
    ])


# this route is for doctor to see the availability of doctor and booked slots
@doctor_bp.route("/availability/<int:doctor_id>", methods=["GET"])
@jwt_required()
def get_doctor_availability(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if not doctor.availability:
        return jsonify({}), 200

    result = {}

    for d, slots in doctor.availability.items():
        selected_date = date.fromisoformat(d)

        result[d] = [
            {
                "time": t,
                "booked": Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    db.func.date(Appointment.appointment_time) == selected_date,
                    db.func.strftime('%H:%M', Appointment.appointment_time) == t
                ).first() is not None
            }
            for t in slots
        ]

    return jsonify(result), 200
