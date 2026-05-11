import sys
import os

# Add project root directory to Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import pandas as pd

from app import create_app, db
from app.models import (
    Region,
    Provider,
    MonthlyActivity
)

# Create Flask application
app = create_app()


# Convert invalid values safely to integers
def safe_int(value):
    try:
        if pd.isna(value):
            return 0

        # Handle NHS hidden values like '*'
        value = str(value).replace(",", "").replace("*", "").strip()

        if value == "":
            return 0

        return int(float(value))

    except:
        return 0


with app.app_context():

    print("Loading NHS activity data...")

    # Read NHS CSV file
    df = pd.read_csv(
        "data/HES MAR 2020-21 M13.csv",
        encoding="latin1"
    )

    # Standardise all column names
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
    )

    # Print columns for debugging
    print(df.columns.tolist())

    print(f"Original rows: {len(df)}")

    # Keep only provider-level records
    df = df[df["ORGANISATION_BREAKDOWN"] == "Provider"]

    print(f"Provider rows: {len(df)}")

    # Limit rows for assignment requirement
    df = df.head(5000)

    print(f"Rows selected: {len(df)}")

    # Loop through dataset rows
    for _, row in df.iterrows():

        # Get region information
        region_name = str(row.get("REGION_NAME", "Unknown")).strip()
        region_code = str(row.get("REGION_CODE", "UNKNOWN")).strip()

        # Create/find region
        region = Region.query.filter_by(region_code=region_code).first()

        if not region:
            region = Region(
                region_code=region_code,
                region_name=region_name
            )

            db.session.add(region)
            db.session.flush()

        # Get provider information
        org_code = str(row.get("ORG_CODE", "")).strip()
        org_name = str(row.get("ORG_NAME", "")).strip()

        # Skip invalid providers
        if not org_code or not org_name:
            continue

        # Create/find provider
        provider = Provider.query.filter_by(org_code=org_code).first()

        if not provider:

            provider = Provider(
                org_code=org_code,
                org_name=org_name,
                organisation_breakdown=row.get("ORGANISATION_BREAKDOWN"),
                region=region
            )

            db.session.add(provider)
            db.session.flush()

        # Create monthly activity record
        activity = MonthlyActivity(

            provider=provider,

            financial_year=str(row.get("FINANCIAL_YEAR", "")),
            reporting_period=safe_int(row.get("REPORTING_PERIOD")),
            activity_month=str(row.get("ACTIVITY_MONTH", "")),

            # Specific specialty activity
            specific_ordinary_elective=safe_int(
                row.get("SPECIFIC_ORDINARY_ELECTIVE")
            ),

            specific_daycase_elective=safe_int(
                row.get("SPECIFIC_DAYCASE_ELECTIVE")
            ),

            specific_elective_total=safe_int(
                row.get("SPECIFIC_ELECTIVE_TOTAL")
            ),

            specific_non_elective=safe_int(
                row.get("SPECIFIC_NON_ELECTIVE")
            ),

            specific_first_gp=safe_int(
                row.get("SPECIFIC_FIRST_GP")
            ),

            specific_first_other=safe_int(
                row.get("SPECIFIC_FIRST_OTHER")
            ),

            specific_first_total=safe_int(
                row.get("SPECIFIC_FIRST_TOTAL")
            ),

            specific_first_dna=safe_int(
                row.get("SPECIFIC_FIRST_DNA")
            ),

            specific_subsequent_seen=safe_int(
                row.get("SPECIFIC_SUBSEQUENT_SEEN")
            ),

            specific_subsequent_dna=safe_int(
                row.get("SPECIFIC_SUBSEQUENT_DNA")
            ),

            # All specialty activity
            all_ordinary_elective=safe_int(
                row.get("ALL_ORDINARY_ELECTIVE")
            ),

            all_daycase_elective=safe_int(
                row.get("ALL_DAYCASE_ELECTIVE")
            ),

            all_elective_total=safe_int(
                row.get("ALL_ELECTIVE_TOTAL")
            ),

            all_non_elective=safe_int(
                row.get("ALL_NON_ELECTIVE")
            ),

            all_first_gp=safe_int(
                row.get("ALL_FIRST_GP")
            ),

            all_first_other=safe_int(
                row.get("ALL_FIRST_OTHER")
            ),

            all_first_total=safe_int(
                row.get("ALL_FIRST_TOTAL")
            ),

            all_first_dna=safe_int(
                row.get("ALL_FIRST_DNA")
            ),

            all_subsequent_seen=safe_int(
                row.get("ALL_SUBSEQUENT_SEEN")
            ),

            all_subsequent_dna=safe_int(
                row.get("ALL_SUBSEQUENT_DNA")
            ),
        )

        db.session.add(activity)

    # Save all records
    db.session.commit()

    print("NHS provider activity data imported successfully!")