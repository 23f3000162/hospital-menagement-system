import csv
from tasks.celery_worker import celery
from models import Doctor, Appointment
from app import create_app
import os


@celery.task(name="task.monthly_doctor_report")
def monthly_doctor_report():
    app = create_app()

    with app.app_context():   # celery flask se alag  run hota h therefore database ko access krne ke liye application contex push krna padtha h 
        os.makedirs("reports", exist_ok=True)
        file_path = "reports/monthly_report.csv"   # set the file path 

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Doctor ID", "Doctor Name", "Completed Appointments"]) # header  set kiya

            doctors = Doctor.query.all()  # all doctors ko featch kiya from the database
            for doctor in doctors:
                total = Appointment.query.filter_by(
                    doctor_id=doctor.id,
                    status="Completed"
                ).count()

                writer.writerow([doctor.id, doctor.full_name, total])

        print("[MONTHLY REPORT] CSV generated")
