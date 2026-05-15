import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import (
    AgeBandActivity,
    MonthlyActivity,
    Provider,
    Region,
    TreatmentSpecialty,
    TreatmentSpecialtyActivity,
)


@pytest.fixture()
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()
        seed_test_data()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Create a Flask test client for route tests."""
    return app.test_client()


def seed_test_data():
    """Insert small but realistic NHS test data."""

    north = Region(region_code="N01", region_name="north east")
    south = Region(region_code="S01", region_name="south west")

    db.session.add_all([north, south])
    db.session.flush()

    alpha = Provider(org_code="A001", org_name="Alpha NHS Trust", region=north)
    beta = Provider(org_code="B001", org_name="Beta NHS Trust", region=north)
    gamma = Provider(org_code="C001", org_name="Gamma NHS Trust", region=south)

    db.session.add_all([alpha, beta, gamma])
    db.session.flush()

    db.session.add_all(
        [
            MonthlyActivity(
                provider=alpha,
                financial_year="2020/21",
                reporting_period=1,
                activity_month="April",
                all_elective_total=100,
                all_non_elective=50,
                all_first_total=200,
                all_subsequent_seen=100,
                all_first_dna=10,
                all_subsequent_dna=5,
            ),
            MonthlyActivity(
                provider=alpha,
                financial_year="2020/21",
                reporting_period=2,
                activity_month="April",
                all_elective_total=50,
                all_non_elective=25,
                all_first_total=100,
                all_subsequent_seen=50,
                all_first_dna=5,
                all_subsequent_dna=0,
            ),
            MonthlyActivity(
                provider=beta,
                financial_year="2020/21",
                reporting_period=1,
                activity_month="May",
                all_elective_total=500,
                all_non_elective=250,
                all_first_total=600,
                all_subsequent_seen=300,
                all_first_dna=45,
                all_subsequent_dna=15,
            ),
            MonthlyActivity(
                provider=gamma,
                financial_year="2020/21",
                reporting_period=1,
                activity_month="June",
                all_elective_total=10,
                all_non_elective=5,
                all_first_total=0,
                all_subsequent_seen=0,
                all_first_dna=0,
                all_subsequent_dna=0,
            ),
        ]
    )

    db.session.add_all(
        [
            AgeBandActivity(
                age_band="01. 0 - 4",
                emergency=100,
                total_appointments=200,
                attended_appointments=180,
                dna_appointments=20,
            ),
            AgeBandActivity(
                age_band="02. 5 - 9",
                emergency=50,
                total_appointments=0,
                attended_appointments=0,
                dna_appointments=0,
            ),
            AgeBandActivity(
                age_band="90+",
                emergency=10,
                total_appointments=100,
                attended_appointments=95,
                dna_appointments=5,
            ),
        ]
    )

    cardiology = TreatmentSpecialty(
        specialty_code="320",
        specialty_name="Cardiology",
    )

    surgery = TreatmentSpecialty(
        specialty_code="100",
        specialty_name="General Surgery",
    )

    db.session.add_all([cardiology, surgery])
    db.session.flush()

    db.session.add_all(
        [
            TreatmentSpecialtyActivity(
                specialty=cardiology,
                emergency=300,
                total_appointments=1000,
                attended_appointments=950,
                dna_appointments=50,
                latest_month_flag=1,
            ),
            TreatmentSpecialtyActivity(
                specialty=surgery,
                emergency=200,
                total_appointments=0,
                attended_appointments=0,
                dna_appointments=0,
                latest_month_flag=1,
            ),
        ]
    )

    db.session.commit()