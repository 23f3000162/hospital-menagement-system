from extensions import db


class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)

    # Link to appointment
    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.id"),
        nullable=False
    )

    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Relationship to Appointment
    appointment = db.relationship(
        "Appointment",
        backref=db.backref("treatments", lazy=True)
    )
