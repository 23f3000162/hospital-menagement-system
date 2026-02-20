from flask_mail import Message
from extensions import mail
from tasks.celery_worker import celery


@celery.task(name="tasks.send_email.send_email")
def send_email(subject, recipients, body):

    from app import create_app
    app = create_app()

    with app.app_context():

        # 👇 YAHAN APNA FIXED EMAIL DAAL DO
        admin_email = "anshusharma3540@gmail.com"

        # 👇 Agar patient ka mail bhi bhejna ho to
        final_recipients = [admin_email]

        # optional: patient mail bhi add ho jaye
        if recipients:
            final_recipients.extend(recipients)

        msg = Message(
            subject=subject,
            sender=app.config["MAIL_USERNAME"],
            recipients=final_recipients,
            body=body
        )

        mail.send(msg)




@celery.task(name="tasks.send_email.send_reminder_email")
def send_reminder_email(subject, recipients, body):
    from app import create_app
    app = create_app()

    with app.app_context():
        msg = Message(
            subject=subject,
            sender=app.config["MAIL_USERNAME"],
            recipients=recipients,
            body=body
        )
        mail.send(msg)
