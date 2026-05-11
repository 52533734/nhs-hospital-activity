from app import create_app, db
from app.models import (
    Region,
    Provider,
    MonthlyActivity,
    TreatmentSpecialty,
    TreatmentSpecialtyActivity,
    AgeBandActivity
)

# Create Flask app
app = create_app()

# Create all database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")