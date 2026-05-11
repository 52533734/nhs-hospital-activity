from flask import Blueprint, render_template, request
from app import db
from app.models import Provider, Region, MonthlyActivity

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