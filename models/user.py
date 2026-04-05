
import uuid
from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    language = db.Column(db.String(5), default="en", nullable=False)  # en / es
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    profile = db.relationship(
        "Profile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    action_progress = db.relationship(
        "ActionProgress",
        backref="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Q1 — Life Situation (multi-select)
    # Must support:
    # - full_time_student
    # - working_professional
    # - student_working
    # - recently_graduated
    # - new_to_country
    # - self_employed_gig_worker
    # - staying_with_family_no_fixed_income
    life_situations = db.Column(db.JSON, nullable=False, default=list)

    # Smart sub-options from Q1
    is_student = db.Column(db.Boolean, nullable=False, default=False)
    is_international = db.Column(db.Boolean, nullable=False, default=False)
    country_of_origin = db.Column(db.String(100), nullable=True)
    entry_route = db.Column(db.String(50), nullable=True)
    # suggested values:
    # work_visa, student_visa, family_sponsorship,
    # asylum_refugee, permanent_resident

    # Q2 — Income Sources (multi-select)
    # Suggested values:
    # full_time_employment, on_campus_job, part_time_job,
    # gig_delivery_work, freelance_contract_work,
    # scholarship_financial_aid, parent_family_funding,
    # government_assistance, investments_passive_income,
    # no_income
    income_sources = db.Column(db.JSON, nullable=False, default=list)

    # Q3
    housing_type = db.Column(db.String(50), nullable=True)
    # suggested values:
    # rent, own, dorm, with_family, temporary, other

    # Q4–Q6
    has_health_insurance = db.Column(db.Boolean, nullable=False, default=False)
    has_auto_insurance = db.Column(db.Boolean, nullable=False, default=False)
    has_emergency_fund = db.Column(db.Boolean, nullable=False, default=False)

    # Optional derived/helper fields for business logic
    needs_renters_insurance = db.Column(db.Boolean, nullable=False, default=False)
    likely_gig_driver = db.Column(db.Boolean, nullable=False, default=False)

    # Computed fields
    risk_score = db.Column(db.Integer, nullable=False, default=0)
    risk_level = db.Column(db.String(20), nullable=False, default="low")
    biggest_risk = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class ActionProgress(db.Model):
    __tablename__ = "action_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_key = db.Column(db.String(100), nullable=False, index=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
