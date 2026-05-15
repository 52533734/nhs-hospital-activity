import sys
import os

# Add project root directory to Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

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