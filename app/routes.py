from flask import Blueprint, render_template, request
from app import db
from app.models import Provider, Region, MonthlyActivity
from app.services import (
    top_10_busiest_providers,
    average_emergency_by_region,
    highest_outpatient_attendance,
    highest_dna_appointments
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

    # Get provider activity records
    activities = provider.monthly_activities

    # Send data to template
    return render_template(
        "provider_detail.html",
        provider=provider,
        activities=activities
    )

@main.route("/analytics")
def analytics():
    # Load analytics results
    busiest_providers = top_10_busiest_providers()
    emergency_by_region = average_emergency_by_region()
    outpatient_attendance = highest_outpatient_attendance()
    dna_appointments = highest_dna_appointments()

    # Send analytics data to template
    return render_template(
        "analytics.html",
        busiest_providers=busiest_providers,
        emergency_by_region=emergency_by_region,
        outpatient_attendance=outpatient_attendance,
        dna_appointments=dna_appointments
    )


@main.route("/compare")
def compare():
    # Get selected provider IDs from URL
    provider1_id = request.args.get("provider1", type=int)
    provider2_id = request.args.get("provider2", type=int)
    provider3_id = request.args.get("provider3", type=int)

    # Load all providers for dropdown menus
    providers = Provider.query.order_by(Provider.org_name).all()

    # Store selected provider summaries
    selected_providers = []

    # Load provider 1 if selected
    if provider1_id:
        provider1 = Provider.query.get(provider1_id)
        if provider1:
            selected_providers.append(provider_summary(provider1))

    # Load provider 2 if selected
    if provider2_id:
        provider2 = Provider.query.get(provider2_id)
        if provider2:
            selected_providers.append(provider_summary(provider2))

    # Load provider 3 if selected
    if provider3_id:
        provider3 = Provider.query.get(provider3_id)
        if provider3:
            selected_providers.append(provider_summary(provider3))

    # Send comparison data to template
    return render_template(
        "compare.html",
        providers=providers,
        selected_providers=selected_providers,
        provider1_id=provider1_id,
        provider2_id=provider2_id,
        provider3_id=provider3_id
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