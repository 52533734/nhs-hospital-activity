from app import db
from app.models import Provider, Region, MonthlyActivity, AgeBandActivity, TreatmentSpecialty, TreatmentSpecialtyActivity


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

def age_band_summary():
    # Summarise NHS activity grouped by age band
    return db.session.query(
        AgeBandActivity.age_band.label("age_band"),
        db.func.sum(AgeBandActivity.emergency).label("total_emergency"),
        db.func.sum(AgeBandActivity.total_appointments).label("total_appointments"),
        db.func.sum(AgeBandActivity.attended_appointments).label("attended_appointments"),
        db.func.sum(AgeBandActivity.dna_appointments).label("dna_appointments")
    ).group_by(
        AgeBandActivity.age_band
    ).order_by(
        db.desc("total_emergency")
    ).all()


def age_band_dna_rates():
    # Calculate DNA rate by age band
    results = age_band_summary()

    # Build formatted list of age-band DNA rates
    return [
        {
            "age_band": row.age_band,
            "total_appointments": row.total_appointments or 0,
            "dna_appointments": row.dna_appointments or 0,
            "dna_rate": round(
                ((row.dna_appointments or 0) / row.total_appointments) * 100,
                2
            ) if row.total_appointments else 0
        }
        for row in results
    ]


def age_best_and_worst_dna_rates():
    # Get age DNA rate results
    rates = age_band_dna_rates()

    # Sort age groups by DNA rate
    sorted_rates = sorted(
        rates,
        key=lambda item: item["dna_rate"],
        reverse=True
    )

    # Return worst and best age bands
    return {
        "worst": sorted_rates[:5],
        "best": sorted_rates[-5:][::-1]
    }


def highest_emergency_age_bands():
    # Return age bands with highest emergency activity
    return db.session.query(
        AgeBandActivity.age_band.label("age_band"),
        db.func.sum(AgeBandActivity.emergency).label("total_emergency")
    ).group_by(
        AgeBandActivity.age_band
    ).order_by(
        db.desc("total_emergency")
    ).limit(10).all()


def dashboard_totals():
    #Calculate overall dashboard totals
    return {
        "providers": Provider.query.count(),
        "regions": Region.query.count(),
        "total_admissions": db.session.query(
            db.func.sum(MonthlyActivity.all_elective_total + MonthlyActivity.all_non_elective)
        ).scalar() or 0,
        "total_dna": db.session.query(
            db.func.sum(MonthlyActivity.all_first_dna + MonthlyActivity.all_subsequent_dna)
        ).scalar() or 0
    }


def provider_performance_rankings():
    # Rank providers by lower DNA rate and higher activity
    results = db.session.query(
        Provider.org_name.label("org_name"),
        Region.region_name.label("region_name"),
        db.func.sum(
            MonthlyActivity.all_elective_total + MonthlyActivity.all_non_elective
        ).label("total_admissions"),
        db.func.sum(
            MonthlyActivity.all_first_total + MonthlyActivity.all_subsequent_seen
        ).label("total_outpatients"),
        db.func.sum(
            MonthlyActivity.all_first_dna + MonthlyActivity.all_subsequent_dna
        ).label("total_dna")
    ).join(
        Region
    ).join(
        MonthlyActivity
    ).group_by(
        Provider.id,
        Provider.org_name,
        Region.region_name
    ).all()

    # Build ranked provider performance list
    ranked = []

    # Loop through provider results
    for row in results:

        # Calculate total appointments
        total_appointments = row.total_outpatients or 0

        # Calculate DNA rate
        dna_rate = round(
            ((row.total_dna or 0) / total_appointments) * 100,
            2
        ) if total_appointments else 0

        # Calculate simple performance score
        performance_score = round(
            (100 - dna_rate) + ((row.total_admissions or 0) / 10000),
            2
        )

        # Store provider ranking data
        ranked.append({
            "org_name": row.org_name,
            "region_name": row.region_name,
            "total_admissions": row.total_admissions or 0,
            "total_outpatients": row.total_outpatients or 0,
            "total_dna": row.total_dna or 0,
            "dna_rate": dna_rate,
            "performance_score": performance_score
        })

    # Sort best providers first
    return sorted(
        ranked,
        key=lambda item: item["performance_score"],
        reverse=True
    )


def best_and_worst_providers():
    # Get ranked provider performance list
    rankings = provider_performance_rankings()

    # Return best and worst providers
    return {
        "best": rankings[:10],
        "worst": rankings[-10:][::-1]
    }


def specialty_summary():
    # Summarise activity by treatment specialty
    return db.session.query(

        # Get treatment specialty name
        TreatmentSpecialty.specialty_name.label("specialty_name"),

        # Calculate total emergency activity
        db.func.sum(
            TreatmentSpecialtyActivity.emergency
        ).label("total_emergency"),

        # Calculate total appointments
        db.func.sum(
            TreatmentSpecialtyActivity.total_appointments
        ).label("total_appointments"),

        # Calculate attended appointments
        db.func.sum(
            TreatmentSpecialtyActivity.attended_appointments
        ).label("attended_appointments"),

        # Calculate DNA appointments
        db.func.sum(
            TreatmentSpecialtyActivity.dna_appointments
        ).label("dna_appointments")

    ).join(
        TreatmentSpecialtyActivity
    ).group_by(
        TreatmentSpecialty.id,
        TreatmentSpecialty.specialty_name
    ).order_by(
        db.desc("total_appointments")
    ).limit(10).all()


def specialty_dna_rates():
    # Calculate DNA rate by treatment specialty
    rows = specialty_summary()

    # Build specialty DNA rate list
    return [
        {
            "specialty_name": row.specialty_name,
            "total_appointments": row.total_appointments or 0,
            "dna_appointments": row.dna_appointments or 0,
            "dna_rate": round(
                ((row.dna_appointments or 0) / row.total_appointments) * 100,
                2
            ) if row.total_appointments else 0
        }
        for row in rows
    ]


def provider_detail_totals(provider):
    # Calculate provider-level totals
    total_admissions = sum(
        (a.all_elective_total or 0) + (a.all_non_elective or 0)
        for a in provider.monthly_activities
    )

    # Calculate outpatient total
    total_outpatients = sum(
        (a.all_first_total or 0) + (a.all_subsequent_seen or 0)
        for a in provider.monthly_activities
    )

    # Calculate DNA total
    total_dna = sum(
        (a.all_first_dna or 0) + (a.all_subsequent_dna or 0)
        for a in provider.monthly_activities
    )

    # Calculate DNA percentage
    dna_rate = round((total_dna / total_outpatients) * 100, 2) if total_outpatients else 0

    # Return provider totals
    return {
        "total_admissions": total_admissions,
        "total_outpatients": total_outpatients,
        "total_dna": total_dna,
        "dna_rate": dna_rate
    }
