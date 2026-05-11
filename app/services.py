from app import db
from app.models import Provider, Region, MonthlyActivity


def top_10_busiest_providers():
    # Get providers with the highest total admissions
    return db.session.query(
        Provider.org_name.label("org_name"),
        Region.region_name.label("region_name"),
        db.func.sum(
            MonthlyActivity.all_elective_total + MonthlyActivity.all_non_elective
        ).label("total_admissions")
    ).select_from(Provider).join(
        MonthlyActivity,
        MonthlyActivity.provider_id == Provider.id
    ).join(
        Region,
        Provider.region_id == Region.id
    ).group_by(
        Provider.id,
        Provider.org_name,
        Region.region_name
    ).order_by(
        db.desc("total_admissions")
    ).limit(10).all()


def average_emergency_by_region():
    # Get average emergency admissions grouped by region
    return db.session.query(
        Region.region_name.label("region_name"),
        db.func.avg(MonthlyActivity.all_non_elective).label("average_emergency")
    ).select_from(Region).join(
        Provider,
        Provider.region_id == Region.id
    ).join(
        MonthlyActivity,
        MonthlyActivity.provider_id == Provider.id
    ).group_by(
        Region.id,
        Region.region_name
    ).order_by(
        db.desc("average_emergency")
    ).all()


def highest_outpatient_attendance():
    # Get providers with the highest outpatient attendance
    return db.session.query(
        Provider.org_name.label("org_name"),
        Region.region_name.label("region_name"),
        db.func.sum(
            MonthlyActivity.all_first_total + MonthlyActivity.all_subsequent_seen
        ).label("total_outpatients")
    ).select_from(Provider).join(
        MonthlyActivity,
        MonthlyActivity.provider_id == Provider.id
    ).join(
        Region,
        Provider.region_id == Region.id
    ).group_by(
        Provider.id,
        Provider.org_name,
        Region.region_name
    ).order_by(
        db.desc("total_outpatients")
    ).limit(10).all()


def highest_dna_appointments():
    # Get providers with the highest missed appointments
    return db.session.query(
        Provider.org_name.label("org_name"),
        Region.region_name.label("region_name"),
        db.func.sum(
            MonthlyActivity.all_first_dna + MonthlyActivity.all_subsequent_dna
        ).label("total_dna")
    ).select_from(Provider).join(
        MonthlyActivity,
        MonthlyActivity.provider_id == Provider.id
    ).join(
        Region,
        Provider.region_id == Region.id
    ).group_by(
        Provider.id,
        Provider.org_name,
        Region.region_name
    ).order_by(
        db.desc("total_dna")
    ).limit(10).all()

def provider_summary(provider):
    # Calculate summary totals for one provider
    activities = provider.monthly_activities

    # Return calculated totals
    return {
        "name": provider.org_name,
        "region": provider.region.region_name if provider.region else "Unknown",
        "elective_admissions": sum(a.all_elective_total or 0 for a in activities),
        "emergency_admissions": sum(a.all_non_elective or 0 for a in activities),
        "outpatient_attendance": sum(
            (a.all_first_total or 0) + (a.all_subsequent_seen or 0)
            for a in activities
        ),
        "dna_appointments": sum(
            (a.all_first_dna or 0) + (a.all_subsequent_dna or 0)
            for a in activities
        )
    }