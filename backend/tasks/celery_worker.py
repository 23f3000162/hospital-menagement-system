from celery import Celery  # use to run background tasks
# Using Celery prevents blocking the main request and improves system performance

celery = Celery(     # Broker is used to send tasks to workers, and backend is used to store task results
    "hms_tasks",
    broker="redis://127.0.0.1:6379/0",  # Broker = message transporter (brockr hia yaha redis)
    backend="redis://127.0.0.1:6379/0",
    include=[
        "tasks.export_csv",
        "tasks.daily_reminder",
        "tasks.monthly_report",
        "tasks.send_email"
    ]
)

celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False
)


# app will send the task to redis brockr and worker will pick the task from redis broker and execute it
# and bad me jo result aata h wo redis backend me store ho jata h