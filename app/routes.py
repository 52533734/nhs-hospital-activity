from flask import Blueprint, render_template, request
from app import db
from app.models import Provider, Region, MonthlyActivity
from app.services import (
    top_10_busiest_providers,
    average_emergency_by_region,
    highest_outpatient_attendance,
    highest_dna_appointments,
    age_band_summary,
    age_band_dna_rates,
    highest_emergency_age_bands,
    age_best_and_worst_dna_rates,
    dashboard_totals,
    provider_performance_rankings,
    best_and_worst_providers,
    specialty_summary,
    specialty_dna_rates,
    provider_detail_totals
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

    # Load provider performance rankings
    performance_rankings = provider_performance_rankings()

    return render_template(
        "providers.html",
        providers=providers,
        regions=regions,
        search=search,
        selected_region=region_id,
        min_admissions=min_admissions,
        min_outpatients=min_outpatients,
        performance_rankings=performance_rankings
    )


@main.route("/providers/<int:provider_id>")
def provider_detail(provider_id):

    # Find provider by ID
    provider = Provider.query.get_or_404(provider_id)

    # Get provider activity records
    activities = provider.monthly_activities

    # Calculate provider totals
    totals = provider_detail_totals(provider)

    # Send data to template
    return render_template(
        "provider_detail.html",
        provider=provider,
        activities=activities,
        totals=totals
    )


@main.route("/analytics")
def analytics():
    # Load analytics results
    busiest_providers = top_10_busiest_providers()
    emergency_by_region = average_emergency_by_region()
    outpatient_attendance = highest_outpatient_attendance()
    dna_appointments = highest_dna_appointments()

    # Load dashboard summary totals
    totals = dashboard_totals()

    # Load best and worst provider performance
    provider_cases = best_and_worst_providers()

    # Load specialty activity summary
    specialties = specialty_summary()

    # Load specialty DNA rates
    specialty_rates = specialty_dna_rates()

    # Send analytics data to template
    return render_template(
        "analytics.html",
        busiest_providers=busiest_providers,
        emergency_by_region=emergency_by_region,
        outpatient_attendance=outpatient_attendance,
        dna_appointments=dna_appointments,
        provider_cases=provider_cases,
        specialties=specialties,
        specialty_rates=specialty_rates,
        totals=totals
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