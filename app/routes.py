from flask import Blueprint, render_template, request
from app.models import Provider

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/providers")
def providers():
    # Get page number from URL, default to page 1
    page = request.args.get("page", 1, type=int)

    # Get providers from database and split into pages
    providers = Provider.query.order_by(
        Provider.org_name
    ).paginate(
        page=page,
        per_page=25,
        error_out=False
    )

    # Send provider data to template
    return render_template(
        "providers.html",
        providers=providers
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