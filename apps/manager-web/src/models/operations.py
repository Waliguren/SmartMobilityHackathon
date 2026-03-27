from src import db


class Technician(db.Model):
    __tablename__ = "technicians"

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    zone = db.Column(db.String(120), nullable=False)
    expertise = db.Column(db.Integer, default=0, nullable=False)
    expert = db.Column(db.Boolean, default=False, nullable=False)

    visits = db.relationship("Visit", back_populates="technician", lazy="select")
    reports = db.relationship("Report", back_populates="technician", lazy="select")


class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.String(40), primary_key=True)
    client_id = db.Column(db.String(120), nullable=False)
    charger_id = db.Column(db.String(40), nullable=False, index=True)
    contract_type = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.String(40), nullable=False)


class Incidence(db.Model):
    __tablename__ = "incidences"

    id = db.Column(db.String(40), primary_key=True)
    charger_id = db.Column(db.String(40), nullable=False, index=True)
    priority = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime)

    visits = db.relationship("Visit", back_populates="incidence", lazy="select")


class Visit(db.Model):
    __tablename__ = "visits"

    id = db.Column(db.String(40), primary_key=True)
    technician_id = db.Column(db.String(20), db.ForeignKey("technicians.id"))
    incidence_id = db.Column(db.String(40), db.ForeignKey("incidences.id"), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    visit_type = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    planned_date = db.Column(db.DateTime)

    technician = db.relationship("Technician", back_populates="visits", lazy="select")
    incidence = db.relationship("Incidence", back_populates="visits", lazy="select")
    reports = db.relationship("Report", back_populates="visit", lazy="select")


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.String(40), primary_key=True)
    visit_id = db.Column(db.String(40), db.ForeignKey("visits.id"), nullable=False)
    technician_id = db.Column(db.String(20), db.ForeignKey("technicians.id"), nullable=False)
    report_type = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    observations = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime)

    visit = db.relationship("Visit", back_populates="reports", lazy="select")
    technician = db.relationship("Technician", back_populates="reports", lazy="select")
