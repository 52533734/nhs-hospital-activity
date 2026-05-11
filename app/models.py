from app import db


# Stores NHS regional information
class Region(db.Model):
    __tablename__ = "regions"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # NHS region code
    region_code = db.Column(db.String(20), unique=True, nullable=False)

    # Region name
    region_name = db.Column(db.String(150), nullable=False)

    # Relationship with providers
    providers = db.relationship("Provider", back_populates="region", lazy=True)

    def __repr__(self):
        return f"<Region {self.region_name}>"


# Stores NHS provider/trust information
class Provider(db.Model):
    __tablename__ = "providers"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Organisation code from NHS dataset
    org_code = db.Column(db.String(20), unique=True, nullable=False)

    # Provider/trust name
    org_name = db.Column(db.String(200), nullable=False)

    # Organisation type/category
    organisation_breakdown = db.Column(db.String(100))

    # Foreign key linking provider to region
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"), nullable=True)

    # Relationship with region table
    region = db.relationship("Region", back_populates="providers")

    # Relationship with monthly activity records
    monthly_activities = db.relationship(
        "MonthlyActivity",
        back_populates="provider",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Provider {self.org_name}>"


# Stores monthly provider activity data
class MonthlyActivity(db.Model):
    __tablename__ = "monthly_activities"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking activity to provider
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id"), nullable=False)

    # Financial reporting year
    financial_year = db.Column(db.String(20))

    # NHS reporting period number
    reporting_period = db.Column(db.Integer)

    # Month of activity
    activity_month = db.Column(db.String(20), nullable=False)

    # Elective admission metrics
    specific_ordinary_elective = db.Column(db.Integer, default=0)
    specific_daycase_elective = db.Column(db.Integer, default=0)
    specific_elective_total = db.Column(db.Integer, default=0)

    # Non-elective admission count
    specific_non_elective = db.Column(db.Integer, default=0)

    # First outpatient attendance counts
    specific_first_gp = db.Column(db.Integer, default=0)
    specific_first_other = db.Column(db.Integer, default=0)
    specific_first_total = db.Column(db.Integer, default=0)

    # Missed first appointments (DNA)
    specific_first_dna = db.Column(db.Integer, default=0)

    # Follow-up appointments attended
    specific_subsequent_seen = db.Column(db.Integer, default=0)

    # Missed follow-up appointments
    specific_subsequent_dna = db.Column(db.Integer, default=0)

    # Total elective admissions for all specialties
    all_ordinary_elective = db.Column(db.Integer, default=0)
    all_daycase_elective = db.Column(db.Integer, default=0)
    all_elective_total = db.Column(db.Integer, default=0)

    # Total emergency/non-elective admissions
    all_non_elective = db.Column(db.Integer, default=0)

    # Total first attendances
    all_first_gp = db.Column(db.Integer, default=0)
    all_first_other = db.Column(db.Integer, default=0)
    all_first_total = db.Column(db.Integer, default=0)

    # Total missed first attendances
    all_first_dna = db.Column(db.Integer, default=0)

    # Total follow-up attendances
    all_subsequent_seen = db.Column(db.Integer, default=0)

    # Total missed follow-up attendances
    all_subsequent_dna = db.Column(db.Integer, default=0)

    # Relationship with provider
    provider = db.relationship("Provider", back_populates="monthly_activities")

    # Calculate total admissions
    @property
    def total_admissions(self):
        return (self.all_elective_total or 0) + (self.all_non_elective or 0)

    # Calculate total outpatient attendance
    @property
    def total_outpatient_attendance(self):
        return (self.all_first_total or 0) + (self.all_subsequent_seen or 0)

    # Calculate total DNA appointments
    @property
    def dna_total(self):
        return (self.all_first_dna or 0) + (self.all_subsequent_dna or 0)

    def __repr__(self):
        return f"<MonthlyActivity {self.provider_id} {self.activity_month}>"


# Stores treatment specialty information
class TreatmentSpecialty(db.Model):
    __tablename__ = "treatment_specialties"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # NHS specialty code
    specialty_code = db.Column(db.String(20), unique=True, nullable=False)

    # Specialty name
    specialty_name = db.Column(db.String(200), nullable=False)

    # Relationship with specialty activity records
    activities = db.relationship(
        "TreatmentSpecialtyActivity",
        back_populates="specialty",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<TreatmentSpecialty {self.specialty_name}>"


# Stores monthly activity by treatment specialty
class TreatmentSpecialtyActivity(db.Model):
    __tablename__ = "treatment_specialty_activities"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking to specialty table
    specialty_id = db.Column(
        db.Integer,
        db.ForeignKey("treatment_specialties.id"),
        nullable=False
    )

    # Reporting period information
    part_year = db.Column(db.Integer)
    month_ending = db.Column(db.String(20))
    fy_start_date = db.Column(db.String(20))
    fy_end_date = db.Column(db.String(20))

    # Hospital episode metrics
    fce = db.Column(db.Integer, default=0)
    fces_with_procedure = db.Column(db.Integer, default=0)
    ordinary_admission_episodes = db.Column(db.Integer, default=0)

    # Day case metrics
    fce_day_cases = db.Column(db.Integer, default=0)
    fce_day_with_procedure = db.Column(db.Integer, default=0)

    # Admission and emergency counts
    fae = db.Column(db.Integer, default=0)
    emergency = db.Column(db.Integer, default=0)

    # Outpatient appointment statistics
    total_appointments = db.Column(db.Integer, default=0)
    attended_appointments = db.Column(db.Integer, default=0)
    dna_appointments = db.Column(db.Integer, default=0)

    # Attendance categories
    first_attendance = db.Column(db.Integer, default=0)
    follow_up_attendance = db.Column(db.Integer, default=0)

    # Flag for latest monthly record
    latest_month_flag = db.Column(db.Integer, default=0)

    # Relationship with specialty table
    specialty = db.relationship("TreatmentSpecialty", back_populates="activities")

    def __repr__(self):
        return f"<TreatmentSpecialtyActivity {self.specialty_id} {self.month_ending}>"


# Stores activity grouped by age band
class AgeBandActivity(db.Model):
    __tablename__ = "age_band_activities"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Age category label
    age_band = db.Column(db.String(50), nullable=False)

    # Reporting period information
    part_year = db.Column(db.Integer)
    month_ending = db.Column(db.String(20))
    fy_start_date = db.Column(db.String(20))
    fy_end_date = db.Column(db.String(20))

    # Hospital episode metrics
    fce = db.Column(db.Integer, default=0)
    fces_with_procedure = db.Column(db.Integer, default=0)
    ordinary_admission_episodes = db.Column(db.Integer, default=0)

    # Day case metrics
    fce_day_cases = db.Column(db.Integer, default=0)
    fce_day_with_procedure = db.Column(db.Integer, default=0)

    # Admission and emergency counts
    fae = db.Column(db.Integer, default=0)
    emergency = db.Column(db.Integer, default=0)

    # Outpatient appointment statistics
    total_appointments = db.Column(db.Integer, default=0)
    attended_appointments = db.Column(db.Integer, default=0)
    dna_appointments = db.Column(db.Integer, default=0)

    # Attendance categories
    first_attendance = db.Column(db.Integer, default=0)
    follow_up_attendance = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<AgeBandActivity {self.age_band} {self.month_ending}>"