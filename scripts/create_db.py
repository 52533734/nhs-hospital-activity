from app import create_app, db

# Import all models
from app.models import (
    Region,
    Provider,
    MonthlyActivity,
    TreatmentSpecialty,
    TreatmentSpecialtyActivity,
    AgeBandActivity
)

app = create_app()

with app.app_context():

    # Delete existing tables
    db.drop_all()

    # Recreate all tables
    db.create_all()

    print("Database tables created successfully!")