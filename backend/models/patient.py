from extensions import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    contact = db.Column(db.String(20))
