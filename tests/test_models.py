"""
Tests for database models and calculated properties.
"""

from app.models import MonthlyActivity, Provider, Region


def test_region_provider_relationship(app):
    """Provider should be linked correctly to its NHS region."""
    with app.app_context():
        provider = Provider.query.filter_by(org_code="A001").first()

        assert provider is not None
        assert provider.region is not None
        assert provider.region.region_code == "N01"
        assert provider in provider.region.providers


def test_monthly_activity_calculated_properties_normal_values():
    """MonthlyActivity properties should calculate totals correctly."""
    activity = MonthlyActivity(
        all_elective_total=120,
        all_non_elective=30,
        all_first_total=200,
        all_subsequent_seen=50,
        all_first_dna=5,
        all_subsequent_dna=10,
    )

    assert activity.total_admissions == 150
    assert activity.total_outpatient_attendance == 250
    assert activity.dna_total == 15


def test_monthly_activity_calculated_properties_none_values():
    """None values should be treated as zero."""
    activity = MonthlyActivity(
        all_elective_total=None,
        all_non_elective=None,
        all_first_total=None,
        all_subsequent_seen=None,
        all_first_dna=None,
        all_subsequent_dna=None,
    )

    assert activity.total_admissions == 0
    assert activity.total_outpatient_attendance == 0
    assert activity.dna_total == 0


def test_unique_region_code_constraint_exists():
    """Region code should be unique and required."""
    region_column = Region.__table__.columns["region_code"]

    assert region_column.unique is True
    assert region_column.nullable is False