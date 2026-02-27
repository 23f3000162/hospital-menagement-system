from tasks.celery_worker import celery
from models import Treatment, Appointment
import csv
import os
# User-triggered asynchronous CSV export
# Allows patients to download treatment history
@celery.task(name="task.export_patient_csv")
def export_patient_csv(patient_id):
    from app import create_app

    app = create_app()

    with app.app_context():
        
        results = (
            Treatment.query
            .join(Appointment, Treatment.appointment_id == Appointment.id)
            .filter(Appointment.patient_id == patient_id)
            .all()
        )

        os.makedirs("exports", exist_ok=True)
        file_path = f"exports/patient_{patient_id}_history.csv"

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Patient ID",
                "Doctor ID",
                "Diagnosis",
                "Prescription",
                "Notes"
            ])

            for t in results:
                # get appointment explicitly
                appt = Appointment.query.get(t.appointment_id)

                writer.writerow([
                    patient_id,
                    appt.doctor_id if appt else None,
                    t.diagnosis,
                    t.prescription,
                    t.notes
                ])

        print("[CSV EXPORT] File generated:", file_path)
        return file_path
