import pytest

from app import db
from app.models import AgeBandActivity, Provider
from app.services import (
    admissions_dna_correlation,
    age_band_dna_rates,
    age_band_summary,
    best_and_worst_providers,
    clean_age_band,
    dashboard_totals,
    national_provider_averages,
    percentage,
    provider_detail_totals,
    provider_monthly_summary,
    provider_performance_rankings,
    provider_region_rank,
    specialty_dna_rates,
)


@pytest.mark.parametrize(
    "part, whole, expected",
    [
        (25, 100, 25.0),
        (1, 3, 33.33),
        (0, 100, 0.0),
        (50, 0, 0),
    ],
)
def test_percentage_handles_normal_and_zero_values(part, whole, expected):
    """percentage() should round correctly and avoid division by zero."""
    assert percentage(part, whole) == expected


@pytest.mark.parametrize(
    "raw_age_band, expected",
    [
        ("01. 0 - 4", "0 - 4"),
        ("21. 80 - 84", "80 - 84"),
        ("90+", "90+"),
        ("", "Unknown"),
        (None, "Unknown"),
    ],
)
def test_clean_age_band_removes_numeric_prefix(raw_age_band, expected):
    """Age-band values should display without NHS numeric prefixes."""
    assert clean_age_band(raw_age_band) == expected


def test_dashboard_totals_counts_records_and_activity(app):
    """Dashboard totals should aggregate database activity."""
    with app.app_context():
        totals = dashboard_totals()

    assert totals["providers"] == 3
    assert totals["regions"] == 2
    assert totals["total_admissions"] == 990
    assert totals["total_dna"] == 80


def test_provider_detail_totals_calculates_expected_values(app):
    """Provider detail totals should sum all monthly rows."""
    with app.app_context():
        provider = Provider.query.filter_by(org_code="A001").first()
        totals = provider_detail_totals(provider)

    assert totals["total_admissions"] == 225
    assert totals["total_outpatients"] == 450
    assert totals["total_dna"] == 20
    assert totals["dna_rate"] == 4.44


def test_provider_detail_totals_handles_zero_outpatients(app):
    """DNA rate should be zero if a provider has no outpatient appointments."""
    with app.app_context():
        provider = Provider.query.filter_by(org_code="C001").first()
        totals = provider_detail_totals(provider)

    assert totals["total_outpatients"] == 0
    assert totals["dna_rate"] == 0


def test_provider_monthly_summary_groups_same_month(app):
    """Rows from the same month should be combined."""
    with app.app_context():
        provider = Provider.query.filter_by(org_code="A001").first()
        monthly = provider_monthly_summary(provider)

    assert len(monthly) == 1
    assert monthly[0]["activity_month"] == "April"
    assert monthly[0]["total_admissions"] == 225
    assert monthly[0]["total_outpatient_attendance"] == 450
    assert monthly[0]["dna_total"] == 20


def test_provider_performance_rankings_returns_sorted_results(app):
    """Provider rankings should be sorted by highest score first."""
    with app.app_context():
        rankings = provider_performance_rankings()

    assert len(rankings) == 3
    assert rankings[0]["performance_score"] >= rankings[1]["performance_score"]
    assert rankings[1]["performance_score"] >= rankings[2]["performance_score"]


def test_best_and_worst_providers_returns_lists(app):
    """Best and worst provider analytics should return separate lists."""
    with app.app_context():
        cases = best_and_worst_providers()

    assert "best" in cases
    assert "worst" in cases
    assert len(cases["best"]) <= 10
    assert len(cases["worst"]) <= 10


def test_national_provider_averages_returns_numeric_values(app):
    """National averages should return numeric summary values."""
    with app.app_context():
        averages = national_provider_averages()

    assert averages["average_admissions"] > 0
    assert averages["average_outpatients"] >= 0
    assert averages["average_dna_rate"] >= 0


def test_provider_region_rank_returns_integer(app):
    """Provider should receive a rank inside its own region."""
    with app.app_context():
        provider = Provider.query.filter_by(org_code="A001").first()
        rank = provider_region_rank(provider)

    assert isinstance(rank, int)
    assert rank >= 1


def test_admissions_dna_correlation_valid_range(app):
    """Correlation should stay between -1 and 1."""
    with app.app_context():
        correlation = admissions_dna_correlation()

    assert -1 <= correlation <= 1


def test_admissions_dna_correlation_handles_empty_provider_data(app):
    """Correlation should return zero when there is not enough data."""
    with app.app_context():
        db.session.query(Provider).delete()
        db.session.commit()

        assert admissions_dna_correlation() == 0


def test_age_band_summary_cleans_labels_and_orders_by_emergency(app):
    """Age summaries should clean labels and order by emergency activity."""
    with app.app_context():
        summary = age_band_summary()

    assert summary[0]["age_band"] == "0 - 4"
    assert summary[0]["total_emergency"] == 100
    assert all(not item["age_band"].startswith("01.") for item in summary)


def test_age_band_dna_rates_handles_zero_appointments(app):
    """Age DNA rates should avoid division by zero."""
    with app.app_context():
        rates = age_band_dna_rates()

    zero_case = next(item for item in rates if item["age_band"] == "5 - 9")

    assert zero_case["total_appointments"] == 0
    assert zero_case["dna_rate"] == 0


def test_age_band_summary_handles_empty_table(app):
    """Age summary should return an empty list if no age records exist."""
    with app.app_context():
        db.session.query(AgeBandActivity).delete()
        db.session.commit()

        assert age_band_summary() == []


def test_specialty_dna_rates_handles_zero_appointments(app):
    """Specialty DNA rates should avoid division by zero."""
    with app.app_context():
        rates = specialty_dna_rates()

    surgery = next(
        item for item in rates
        if item["specialty_name"] == "General Surgery"
    )

    assert surgery["total_appointments"] == 0
    assert surgery["dna_rate"] == 0