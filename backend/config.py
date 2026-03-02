import os
from celery.schedules import crontab

class Config:
    SECRET_KEY = "super-secret-key"

    # Redis configuration for Celery broker and result backend
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # dont trackthe history of dta changes each time 
      # sqlalchemy will covert data row in python abject 
    
    JWT_SECRET_KEY = "jwt-secret-key"
    JWT_IDENTITY_CLAIM = "sub"

   
    REDIS_URL = "redis://localhost:6379/0"

    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"

    CELERY_TIMEZONE = "Asia/Kolkata"
    ENABLE_UTC = True   

   
    CELERY_BEAT_SCHEDULE = {
        "daily-appointment-reminder": {
            "task": "task.daily_appointment_reminder",
            "schedule": crontab(hour=8, minute=0),  
        }
    }

    # add commt for push the code on gitub
    MAIL_SERVER = "smtp.gmail.com"    # simple mail transfer protocol server its used to send mail 
    MAIL_PORT = 587   # port number 
    MAIL_USE_TLS = True   # menas encryption use krna h ya nhi
    MAIL_USE_SSL = False
    MAIL_USERNAME = "anshusharma3540@gmail.com"
    MAIL_PASSWORD = "gnqd iafw odpu pnym"  
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
