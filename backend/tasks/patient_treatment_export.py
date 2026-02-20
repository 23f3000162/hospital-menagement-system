import csv
import os
from tasks.celery_worker import celery
from models import Treatment
from models import Treatment, Appointment 


@celery.task(name="task.export_patient_treatments")
def export_patient_treatments(patient_id):
    from app import create_app
    app = create_app()

    with app.app_context():
        os.makedirs("exports", exist_ok=True)
        file_path = f"exports/patient_{patient_id}_treatments.csv"

        treatments = (
            Treatment.query
            .join(Appointment)
            .filter(Appointment.patient_id == patient_id)
            .all()
        )

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Patient ID", "Doctor ID", "Diagnosis", "Prescription", "Notes"])

            for t in treatments:
                writer.writerow([
                    t.appointment.patient_id,
                    t.appointment.doctor_id,
                    t.diagnosis,
                    t.prescription,
                    t.notes
                ])
