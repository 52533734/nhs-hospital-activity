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

    # Get selected provider IDs from URL query parameters
    provider1_id = request.args.get("provider1", type=int)
    provider2_id = request.args.get("provider2", type=int)
    provider3_id = request.args.get("provider3", type=int)

    # Load all providers for dropdown menus
    providers = Provider.query.order_by(Provider.org_name).all()

    # Store only provider IDs that were selected
    selected_ids = [
        pid for pid in [provider1_id, provider2_id, provider3_id] if pid
    ]

    # Store error message if validation fails
    error = None

    # Store provider comparison summaries
    selected_providers = []

    # Check if the same provider was selected more than once
    if len(selected_ids) != len(set(selected_ids)):

        # Show validation error message
        error = "Please select different providers for comparison."

        # Clear selected IDs to stop comparison table rendering
        selected_ids = []

    # Check if user selected only one provider
    if len(selected_ids) == 1:

        # Show validation error message
        error = "Please select at least two providers to compare."

        # Clear selected IDs to stop comparison table rendering
        selected_ids = []

    # Loop through valid provider IDs
    for provider_id in selected_ids:

        # Find provider by ID
        provider = Provider.query.get(provider_id)

        # Check provider exists in database
        if provider:

            # Generate provider summary and add to comparison list
            selected_providers.append(
                provider_summary(provider)
            )

    # Render compare page with all required data
    return render_template(
        "compare.html",
        providers=providers,
        selected_providers=selected_providers,
        provider1_id=provider1_id,
        provider2_id=provider2_id,
        provider3_id=provider3_id,
        error=error
    )