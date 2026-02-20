import csv
import os
from tasks.celery_worker import celery
from models import Appointment


@celery.task(name="task.export_patient_appointments")
def export_patient_appointments(patient_id):
    from app import create_app  

    app = create_app()

    with app.app_context():
        os.makedirs("exports", exist_ok=True)
        file_path = f"exports/patient_{patient_id}_appointments.csv"

        appointments = Appointment.query.filter_by(patient_id=patient_id).all()

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Patient ID", "Doctor ID", "Date", "Time", "Status"
            ])

            for a in appointments:
                writer.writerow([
                    a.patient_id,
                    a.doctor_id,
                    a.date,
                    a.time,
                    a.status
                ])
