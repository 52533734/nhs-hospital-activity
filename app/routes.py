from flask import Blueprint, render_template, request
from app import db
from app.models import Provider, Region, MonthlyActivity
from app.services import (
    dashboard_totals,
    top_10_busiest_providers,
    average_emergency_by_region,
    highest_outpatient_attendance,
    provider_detail_totals,
    national_provider_averages,
    provider_region_rank,
    best_and_worst_providers,
    age_band_summary,
    age_band_dna_rates,
    highest_emergency_age_bands,
    age_best_and_worst_dna_rates,
    specialty_summary,
    specialty_dna_rates,
    admissions_dna_correlation
)
from app.services import provider_summary

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/providers")
def providers():
    # Get current page number
    page = request.args.get("page", 1, type=int)

    # Get search and filter values from URL
    search = request.args.get("search", "")
    region_id = request.args.get("region", "")
    min_admissions = request.args.get("min_admissions", type=int)
    min_outpatients = request.args.get("min_outpatients", type=int)

    # Start provider query
    query = Provider.query

    # Filter by provider name
    if search:
        query = query.filter(Provider.org_name.ilike(f"%{search}%"))

    # Filter by region
    if region_id:
        query = query.filter(Provider.region_id == int(region_id))

    # Filter by minimum admissions
    if min_admissions is not None:
        query = query.join(Provider.monthly_activities).group_by(Provider.id).having(
            db.func.sum(MonthlyActivity.all_elective_total + MonthlyActivity.all_non_elective) >= min_admissions
        )

    # Filter by minimum outpatient attendance
    if min_outpatients is not None:
        query = query.join(Provider.monthly_activities).group_by(Provider.id).having(
            db.func.sum(MonthlyActivity.all_first_total + MonthlyActivity.all_subsequent_seen) >= min_outpatients
        )

    # Paginate filtered results
    providers = query.order_by(Provider.org_name).paginate(
        page=page,
        per_page=25,
        error_out=False
    )

    # Get all regions for dropdown
    regions = Region.query.order_by(Region.region_name).all()


    return render_template(
        "providers.html",
        providers=providers,
        regions=regions,
        search=search,
        selected_region=region_id,
        min_admissions=min_admissions,
        min_outpatients=min_outpatients
    )


@main.route("/providers/<int:provider_id>")
def provider_detail(provider_id):

    # Find provider by ID
    provider = Provider.query.get_or_404(provider_id)

    # Create dictionary to group activity records by month
    monthly_summary = {}

    # Loop through all provider activity records
    for activity in provider.monthly_activities:

        # Store activity month as the grouping key
        month = activity.activity_month

        # Create a new month entry if it does not already exist
        if month not in monthly_summary:
            monthly_summary[month] = {
                "activity_month": month,
                "all_elective_total": 0,
                "all_non_elective": 0,
                "total_admissions": 0,
                "total_outpatient_attendance": 0,
                "dna_total": 0
            }

        # Add elective admissions for this month
        monthly_summary[month]["all_elective_total"] += (
            activity.all_elective_total or 0
        )

        # Add emergency admissions for this month
        monthly_summary[month]["all_non_elective"] += (
            activity.all_non_elective or 0
        )

        # Add total admissions for this month
        monthly_summary[month]["total_admissions"] += (
            (activity.all_elective_total or 0) +
            (activity.all_non_elective or 0)
        )

        # Add outpatient attendance for this month
        monthly_summary[month]["total_outpatient_attendance"] += (
            (activity.all_first_total or 0) +
            (activity.all_subsequent_seen or 0)
        )

        # Add missed appointments for this month
        monthly_summary[month]["dna_total"] += (
            (activity.all_first_dna or 0) +
            (activity.all_subsequent_dna or 0)
        )

    # Convert grouped monthly data into a list
    activities = list(monthly_summary.values())

    # Calculate provider totals
    totals = provider_detail_totals(provider)

    # Calculate national averages
    national_averages = national_provider_averages()

    # Calculate provider rank in its region
    region_rank = provider_region_rank(provider)

    # Send data to template
    return render_template(
        "provider_detail.html",
        provider=provider,
        activities=activities,
        totals=totals,
        national_averages=national_averages,
        region_rank=region_rank
    )


@main.route("/analytics")
def analytics():
    # Load analytics results
    busiest_providers = top_10_busiest_providers()
    emergency_by_region = average_emergency_by_region()
    outpatient_attendance = highest_outpatient_attendance()

    # Load dashboard summary totals
    totals = dashboard_totals()

    # Load best and worst provider performance
    provider_cases = best_and_worst_providers()

    # Load specialty DNA rates
    specialty_rates = specialty_dna_rates()

    # Calculate admissions and DNA correlation
    correlation = admissions_dna_correlation()

    # Send analytics data to template
    return render_template(
        "analytics.html",
        busiest_providers=busiest_providers,
        emergency_by_region=emergency_by_region,
        outpatient_attendance=outpatient_attendance,
        provider_cases=provider_cases,
        specialty_rates=specialty_rates,
        totals=totals,
        correlation=correlation
    )


@main.route("/compare")
def compare():
    # Get selected provider IDs from URL
    provider1_id = request.args.get("provider1", type=int)
    provider2_id = request.args.get("provider2", type=int)
    provider3_id = request.args.get("provider3", type=int)

    # Load all providers for dropdown menus
    providers = Provider.query.order_by(Provider.org_name).all()

    # Store selected IDs that are not empty
    selected_ids = [
        provider_id
        for provider_id in [provider1_id, provider2_id, provider3_id]
        if provider_id
    ]

    # Store validation error message
    error_message = None

    # Check if duplicate providers were selected
    if len(selected_ids) != len(set(selected_ids)):
        error_message = "Please select different providers for comparison."

    # Check at least two providers are selected
    elif len(selected_ids) < 2 and len(selected_ids) > 0:
        error_message = "Please select at least two providers to compare."

    # Store selected provider summaries
    selected_providers = []

    # Only build comparison if there is no validation error
    if not error_message:
        for provider_id in selected_ids:
            provider = Provider.query.get(provider_id)

            if provider:
                selected_providers.append(provider_summary(provider))

    # Send comparison data to template
    return render_template(
        "compare.html",
        providers=providers,
        selected_providers=selected_providers,
        provider1_id=provider1_id,
        provider2_id=provider2_id,
        provider3_id=provider3_id,
        error_message=error_message
    )


@main.route("/age-analytics")
def age_analytics():
    #Load age-band summary data
    age_summary = age_band_summary()

    #Load DNA rate data by age band
    dna_rates = age_band_dna_rates()

    #Load highest emergency age bands
    emergency_age_bands = highest_emergency_age_bands()

    # Load best and worst age-band DNA cases
    age_cases = age_best_and_worst_dna_rates()

    #Render age analytics page
    return render_template(
        "age_analytics.html",
        age_summary=age_summary,
        dna_rates=dna_rates,
        emergency_age_bands=emergency_age_bands,
        age_cases=age_cases
    )


# Handle 404 page not found errors
@main.app_errorhandler(404)
def page_not_found(error):

    # Return custom 404 page
    return render_template(
        "404.html"
    ), 404


# Handle internal server errors
@main.app_errorhandler(500)
def internal_server_error(error):

    # Return custom 500 page
    return render_template(
        "500.html"
    ), 500