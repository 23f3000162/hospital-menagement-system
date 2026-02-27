from extensions import db
from datetime import datetime, date as py_date

# this is the appointment model which will be used to store the appointment details in the database
class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)  #patient_id ka value patients table ke id column se aana chahiye
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)  # nullable flase mtlb ki null value allowed nahi hai appoitemnt jbhi book hogi jb paitent avilabe hoga 

    # Appointment ka actual time
    appointment_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
     # Universal Time Coordinatede (UTC) ka use karte hai taki time zone ke issues na aaye
    status = db.Column(db.String(20), default="Booked")

    # Record kab create hua
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", backref="appointments")
    doctor = db.relationship("Doctor", backref="appointments")
