from datetime import date
from tasks.celery_worker import celery
from models import Appointment
from tasks.send_email import send_email
from app import create_app


@celery.task(name="task.daily_appointment_reminder")
def daily_appointment_reminder():
    app = create_app()

    with app.app_context():
        today = date.today()

        appointments = Appointment.query.filter_by(
            date=today,
            status="Booked"
        ).all()

        if not appointments:
            print("[DAILY REMINDER] No appointments today")
            return "No reminders"

        for appt in appointments:
            patient = appt.patient
            doctor = appt.doctor

            if patient.email:
                send_email.delay(
                    subject="Appointment Reminder",
                    recipients=[patient.email],
                    body=f"""
Hello {patient.username},

Reminder for today's appointment.

Doctor: {doctor.username}
Time: {appt.time}
"""
                )

        print("[DAILY REMINDER] Emails sent")
