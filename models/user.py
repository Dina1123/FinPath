from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    language = db.Column(db.String(5), default="en")  # 'en' or 'es'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("Profile", backref="user", uselist=False)
    action_progress = db.relationship("ActionProgress", backref="user")


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Onboarding quiz answers
    employment_type = db.Column(db.String(50))   # full_time, part_time, gig, unemployed
    income_stability = db.Column(db.String(50))  # stable, variable, none
    has_auto_insurance = db.Column(db.Boolean, default=False)
    has_health_insurance = db.Column(db.Boolean, default=False)
    has_renters_insurance = db.Column(db.Boolean, default=False)
    has_emergency_fund = db.Column(db.Boolean, default=False)
    gig_driving = db.Column(db.Boolean, default=False)
    financial_concern = db.Column(db.String(100))  # insurance, savings, debt, all

    # Computed fields
    risk_score = db.Column(db.Integer, default=0)   # 0–100, higher = more at risk
    risk_level = db.Column(db.String(20), default="low")  # low, medium, high, critical
    biggest_risk = db.Column(db.String(200))

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActionProgress(db.Model):
    __tablename__ = "action_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action_key = db.Column(db.String(100), nullable=False)  # e.g. 'get_auto_insurance'
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
