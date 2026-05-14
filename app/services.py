from app import db
from app.models import Provider, Region, MonthlyActivity, AgeBandActivity, TreatmentSpecialty, TreatmentSpecialtyActivity


def clean_age_band(age_band):
    # Return Unknown if value is empty
    if not age_band:
        return "Unknown"

    # Remove NHS numeric prefix
    parts = str(age_band).split(". ", 1)

    # Return cleaned value if split works
    if len(parts) > 1:
        return parts[1]

    # Return original value if format is unexpected
    return age_band


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

    # Calculate missed appointments(DNA) total
    total_dna = sum(
        (a.all_first_dna or 0) + (a.all_subsequent_dna or 0)
        for a in provider.monthly_activities
    )

    # Calculate missed appointment(DNA) percentage
    dna_rate = round((total_dna / total_outpatients) * 100, 2) if total_outpatients else 0

    # Return provider totals
    return {
        "total_admissions": total_admissions,
        "total_outpatients": total_outpatients,
        "total_dna": total_dna,
        "dna_rate": dna_rate
    }


def provider_performance_rankings():
    # Rank providers by lower missed appointment(DNA) rate and higher activity
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

        # Calculate missed appointment(DNA) rate
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


def national_provider_averages():
    # Calculate national average provider metrics
    providers = provider_performance_rankings()

    # Avoid division by zero
    if not providers:
        return {
            "average_admissions": 0,
            "average_outpatients": 0,
            "average_dna_rate": 0
        }

    # Return national averages
    return {
        "average_admissions": round(
            sum(p["total_admissions"] for p in providers) / len(providers),
            2
        ),
        "average_outpatients": round(
            sum(p["total_outpatients"] for p in providers) / len(providers),
            2
        ),
        "average_dna_rate": round(
            sum(p["dna_rate"] for p in providers) / len(providers),
            2
        )
    }


def provider_region_rank(provider):
    # Rank provider against others in the same region
    rankings = provider_performance_rankings()

    # Keep only providers in the same region
    same_region = [
        p for p in rankings
        if provider.region and p["region_name"] == provider.region.region_name
    ]

    # Find provider rank inside region
    for index, item in enumerate(same_region, start=1):
        if item["org_name"] == provider.org_name:
            return index

    # Return unknown if provider is not found
    return None


def admissions_dna_correlation():
    # Get provider performance data
    providers = provider_performance_rankings()

    # Avoid correlation if there is not enough data
    if len(providers) < 2:
        return 0

    # Get admissions and missed appointment(DNA) values
    admissions = [p["total_admissions"] for p in providers]
    dna = [p["total_dna"] for p in providers]

    # Calculate averages
    avg_admissions = sum(admissions) / len(admissions)
    avg_dna = sum(dna) / len(dna)

    # Calculate numerator
    numerator = sum(
        (admissions[i] - avg_admissions) * (dna[i] - avg_dna)
        for i in range(len(providers))
    )

    # Calculate denominator parts
    admissions_square = sum((x - avg_admissions) ** 2 for x in admissions)
    dna_square = sum((y - avg_dna) ** 2 for y in dna)

    # Avoid division by zero
    if admissions_square == 0 or dna_square == 0:
        return 0

    # Return correlation coefficient
    return round(numerator / ((admissions_square * dna_square) ** 0.5), 2)


def best_and_worst_providers():
    # Get ranked provider performance list
    rankings = provider_performance_rankings()

    # Return best and worst providers
    return {
        "best": rankings[:10],
        "worst": rankings[-10:][::-1]
    }


def age_band_summary():
    # Get NHS activity grouped by age band
    rows = db.session.query(
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

    # Return cleaned age-band labels
    return [
        {
            "age_band": clean_age_band(row.age_band),
            "total_emergency": row.total_emergency or 0,
            "total_appointments": row.total_appointments or 0,
            "attended_appointments": row.attended_appointments or 0,
            "dna_appointments": row.dna_appointments or 0
        }
        for row in rows
    ]


def age_band_dna_rates():
    # Calculate missed appointment(DNA) rate by age band
    results = age_band_summary()

    # Build formatted list of age-band missed appointment(DNA) rates
    return [
        {
            "age_band": row["age_band"],
            "total_appointments": row["total_appointments"],
            "dna_appointments": row["dna_appointments"],
            "dna_rate": round(
                (row["dna_appointments"] / row["total_appointments"]) * 100,
                2
            ) if row["total_appointments"] else 0
        }
        for row in results
    ]


def age_best_and_worst_dna_rates():
    # Get age missed appointment(DNA) rate results
    rates = age_band_dna_rates()

    # Sort age groups by missed appointment(DNA) rate
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
    # Get age bands with highest emergency activity
    rows = db.session.query(
        AgeBandActivity.age_band.label("age_band"),
        db.func.sum(AgeBandActivity.emergency).label("total_emergency")
    ).group_by(
        AgeBandActivity.age_band
    ).order_by(
        db.desc("total_emergency")
    ).limit(10).all()

    # Return cleaned age-band labels
    return [
        {
            "age_band": clean_age_band(row.age_band),
            "total_emergency": row.total_emergency or 0
        }
        for row in rows
    ]


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

        # Calculate missed appointment(DNA) appointments
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
    # Calculate missed appointment(DNA) rate by treatment specialty
    rows = specialty_summary()

    # Build specialty missed appointment(DNA) rate list
    return [
        {
            "specialty_name": row.specialty_name,
            "total_emergency": row.total_emergency or 0,
            "total_appointments": row.total_appointments or 0,
            "dna_appointments": row.dna_appointments or 0,
            "dna_rate": round(
                ((row.dna_appointments or 0) / row.total_appointments) * 100,
                2
            ) if row.total_appointments else 0
        }
        for row in rows
    ]