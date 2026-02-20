import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from flask import Flask, jsonify
from flask_cors import CORS   #  Cross-Origin Resource Sharing tells which frontend can access which backend

from config import Config
from extensions import db, jwt, mail
from models import User, Department
from routes import auth_bp, admin_bp, doctor_bp, patient_bp

# Celery import
from tasks.celery_worker import celery


def make_celery(app):
    """
    Bind Celery with Flask app context
    """
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Bind celery AFTER app is created
    make_celery(app)

    #  Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)

    #  Create DB & seed data
    with app.app_context():
        db.create_all()

        # yaha admin prebuilt hoga agar nahi hai to are nhi h koi mtlb nhi h hme banana hi hia pre build admin
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(username="admin", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

        # Default departments keep in mind ki onley this 3 department work kr rahe h 
        if Department.query.count() == 0:
            db.session.bulk_save_objects([
                Department(name="Cardiology", description="Heart related treatments"),
                Department(name="Oncology", description="Cancer diagnosis and treatment"),
                Department(name="General", description="General physician services")
            ])
            db.session.commit()

    @app.route("/")
    def home():
        return jsonify({"message": "My Hospital Management System"})

    return app



app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
