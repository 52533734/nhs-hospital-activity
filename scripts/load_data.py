import sys
import os

# Add project root directory to Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

# Import pandas for CSV processing
import pandas as pd

# Import Flask app and database
from app import create_app, db

# Import database models
from app.models import (
    Region,
    Provider,
    MonthlyActivity,
    AgeBandActivity, 
    TreatmentSpecialty, 
    TreatmentSpecialtyActivity
)

# Create Flask application instance
app = create_app()


# Safely convert NHS values into integers
def safe_int(value):

    try:

        # Replace missing values with 0
        if pd.isna(value):
            return 0

        # Clean commas, hidden values, and spaces
        value = str(value).replace(",", "").replace("*", "").strip()

        # Replace empty strings with 0
        if value == "":
            return 0

        # Convert value to integer
        return int(float(value))

    except:

        # Return 0 if conversion fails
        return 0


# Start Flask application context
with app.app_context():

    print("Loading NHS activity data...")

    # Read NHS CSV file
    df = pd.read_csv(
        "data/HES MAR 2020-21 M13.csv",
        encoding="latin1"
    )

    # Standardise column names
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
    )

    # Print column names for debugging
    print(df.columns.tolist())

    # Display original row count
    print(f"Original rows: {len(df)}")

    # Keep only provider-level rows
    df = df[df["ORGANISATION_BREAKDOWN"] == "Provider"]

    # Display provider row count
    print(f"Provider rows: {len(df)}")

    # Limit rows for assignment requirement
    df = df.head(2000)

    # Display final row count
    print(f"Rows selected: {len(df)}")

    # Loop through all rows
    for _, row in df.iterrows():

        # Get region name
        region_name = str(
            row.get("REGION_NAME", "Unknown")
        ).strip()

        # Get region code
        region_code = str(
            row.get("REGION_CODE", "UNKNOWN")
        ).strip()

        # Find existing region
        region = Region.query.filter_by(
            region_code=region_code
        ).first()

        # Create region if not found
        if not region:

            region = Region(
                region_code=region_code,
                region_name=region_name
            )

            # Save region temporarily
            db.session.add(region)
            db.session.flush()

        # Get provider code
        org_code = str(
            row.get("ORG_CODE", "")
        ).strip()

        # Get provider name
        org_name = str(
            row.get("ORG_NAME", "")
        ).strip()

        # Skip invalid providers
        if not org_code or not org_name:
            continue

        # Find existing provider
        provider = Provider.query.filter_by(
            org_code=org_code
        ).first()

        # Create provider if not found
        if not provider:

            provider = Provider(

                # Save provider code
                org_code=org_code,

                # Save provider name
                org_name=org_name,

                # Save organisation type
                organisation_breakdown=row.get(
                    "ORGANISATION_BREAKDOWN"
                ),

                # Link provider to region
                region=region
            )

            # Save provider temporarily
            db.session.add(provider)
            db.session.flush()

        # Create monthly activity record
        activity = MonthlyActivity(

            # Link activity to provider
            provider=provider,

            # Save financial year
            financial_year=str(
                row.get("FINANCIAL_YEAR", "")
            ),

            # Save reporting period
            reporting_period=safe_int(
                row.get("REPORTING_PERIOD")
            ),

            # Save activity month
            activity_month=str(
                row.get("ACTIVITY_MONTH", "")
            ),

            # Save specific elective admissions
            specific_ordinary_elective=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_ORDINARY_ELECTIVE"
                )
            ),

            # Save specific day case admissions
            specific_daycase_elective=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_DAYCASE_ELECTIVE"
                )
            ),

            # Save total specific elective admissions
            specific_elective_total=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_ELECTIVE_TOTAL"
                )
            ),

            # Save specific emergency admissions
            specific_non_elective=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_NON-ELECTIVE"
                )
            ),

            # Save GP referral attendances
            specific_first_gp=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_FIRST_ATTENDANCES_SEEN_-_GP_REFERRALS"
                )
            ),

            # Save other referral attendances
            specific_first_other=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_FIRST_ATTENDANCES_SEEN_-_OTHER_REFERRALS"
                )
            ),

            # Save total first attendances
            specific_first_total=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_FIRST_ATTENDANCES_SEEN_TOTAL"
                )
            ),

            # Save missed first attendances
            specific_first_dna=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_FIRST_ATTENDANCES_DNA"
                )
            ),

            # Save follow-up attendances
            specific_subsequent_seen=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_SUBSEQUENT_ATTENDANCES_SEEN"
                )
            ),

            # Save missed follow-up attendances
            specific_subsequent_dna=safe_int(
                row.get(
                    "SPECIFIC_ACUTE_SPECIALTIES:_SUBSEQUENT_ATTENDANCES_DNA"
                )
            ),

            # Save total elective admissions
            all_ordinary_elective=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_ORDINARY_ELECTIVE"
                )
            ),

            # Save total day case admissions
            all_daycase_elective=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_DAYCASE_ELECTIVE"
                )
            ),

            # Save total elective activity
            all_elective_total=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_ELECTIVE_TOTAL"
                )
            ),

            # Save total emergency admissions
            all_non_elective=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_NON-ELECTIVE"
                )
            ),

            # Save total GP referrals
            all_first_gp=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_FIRST_ATTENDANCES_SEEN_-_GP_REFERRALS"
                )
            ),

            # Save total other referrals
            all_first_other=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_FIRST_ATTENDANCES_SEEN_-_OTHER_REFERRALS"
                )
            ),

            # Save total first attendances
            all_first_total=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_FIRST_ATTENDANCES_SEEN_TOTAL"
                )
            ),

            # Save total missed first attendances
            all_first_dna=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_FIRST_ATTENDANCES_DNA"
                )
            ),

            # Save total follow-up attendances
            all_subsequent_seen=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_SUBSEQUENT_ATTENDANCES_SEEN"
                )
            ),

            # Save total missed follow-up attendances
            all_subsequent_dna=safe_int(
                row.get(
                    "ALL_SPECIALTIES:_SUBSEQUENT_ATTENDANCES_DNA"
                )
            ),
        )

        # Add activity record to database session
        db.session.add(activity)

    # Commit provider records after loop finishes
    db.session.commit()

    print("NHS provider activity data imported successfully!")

    # Load age-band NHS activity data
    age_df = pd.read_csv(
        "data/HES_M13_2021_OPEN_DATA_AGE_BANDS.csv",
        encoding="latin1"
    )

    # Standardise age-band column names
    age_df.columns = (
        age_df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
    )

    # Display original age-band row count
    print(f"Age-band rows: {len(age_df)}")
    
    # Limit rows for assignment requirement
    age_df = age_df.head(2000)

    # Print specialty column names for checking
    print(age_df.columns.tolist())
    
    # Loop through age-band rows
    for _, row in age_df.iterrows():
        # Create age-band activity record
        age_activity = AgeBandActivity(
            age_band=str(row.get("AGE_BAND", "Unknown")).strip(),
            part_year=safe_int(row.get("PART_YEAR")),
            month_ending=str(row.get("MONTH_ENDING", "")),
            fy_start_date=str(row.get("FY_START_DATE", "")),
            fy_end_date=str(row.get("FY_END_DATE", "")),
            fce=safe_int(row.get("FCE")),
            fces_with_procedure=safe_int(row.get("FCES_WITH_PROCEDURE")),
            ordinary_admission_episodes=safe_int(row.get("ORDINARY_ADMISSION_EPISODES")),
            fce_day_cases=safe_int(row.get("FCE_DAY_CASES")),
            fce_day_with_procedure=safe_int(row.get("FCE_DAY_WITH_PROCEDURE")),
            fae=safe_int(row.get("FAE")),
            emergency=safe_int(row.get("EMERGENCY")),
            total_appointments=safe_int(row.get("TOTAL_APPOINTMENTS")),
            attended_appointments=safe_int(row.get("ATTENDED_APPOINTMENTS")),
            dna_appointments=safe_int(row.get("DNA_APPOINTMENTS")),
            first_attendance=safe_int(row.get("FIRST_ATTENDANCE")),
            follow_up_attendance=safe_int(row.get("FOLLOW_UP_ATTENDANCE"))
         )
    
        # Add age-band record to database session
        db.session.add(age_activity)

    # Commit age-band records to database
    db.session.commit()
    print("Age-band activity data imported successfully!")


    # Load treatment specialty NHS activity data
    specialty_df = pd.read_csv(
        "data/HES_M13_2021_OPEN_DATA_TREATMENT_FUNCTION.csv",
        encoding="latin1"
    )

    # Standardise specialty column names
    specialty_df.columns = (
        specialty_df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
    )


    # Print specialty column names for checking
    print(specialty_df.columns.tolist())

    # Keep only latest monthly records
    specialty_df = specialty_df[
        (specialty_df["LATEST_MONTH_FLAG"] == 1) &
        (specialty_df["TOTAL_APPOINTMENTS"] > 1000)
    ]

    # Limit rows for assignment requirement
    specialty_df = specialty_df.head(2000)

    # Display final specialty row count
    print(f"Speciality rows selected: {len(specialty_df)}")

    # Loop through specialty rows
    for _, row in specialty_df.iterrows():

        # Get specialty code
        specialty_code = str(row.get("TRETSPEF", "UNKNOWN")).strip()

        # Get specialty name
        specialty_name = str(row.get("TRETSPEF_DESCRIPTION", "Unknown")).strip()
        
        # Find existing specialty
        specialty = TreatmentSpecialty.query.filter_by(
            specialty_code=specialty_code
        ).first()

        # Create specialty if missing
        if not specialty:
            specialty = TreatmentSpecialty(
                specialty_code=specialty_code,
                specialty_name=specialty_name
            )

            # Save specialty before activity link
            db.session.add(specialty)
            db.session.flush()

        # Create treatment specialty activity record
        specialty_activity = TreatmentSpecialtyActivity(
            specialty=specialty,
            part_year=safe_int(row.get("PARTYEAR")),
            month_ending=str(row.get("MONTH_ENDING", "")),
            fy_start_date=str(row.get("FY_START_DATE", "")),
            fy_end_date=str(row.get("FY_END_DATE", "")),
            fce=safe_int(row.get("FCE")),
            fces_with_procedure=safe_int(row.get("FCES_WITH_PROCEDURE")),
            ordinary_admission_episodes=safe_int(row.get("ORDINARY_ADMISSION_EPISODES")),
            fce_day_cases=safe_int(row.get("FCE_DAY_CASES")),
            fce_day_with_procedure=safe_int(row.get("FCE_DAY_WITH_PROCEDURE")),
            fae=safe_int(row.get("FAE")),
            emergency=safe_int(row.get("EMERGENCY")),
            total_appointments=safe_int(row.get("TOTAL_APPOINTMENTS")),
            attended_appointments=safe_int(row.get("ATTENDED_APPOINTMENTS")),
            dna_appointments=safe_int(row.get("DNA_APPOINTMENTS")),
            first_attendance=safe_int(row.get("FIRST_ATTENDANCE")),
            follow_up_attendance=safe_int(row.get("FOLLOW_UP_ATTENDANCE")),
            latest_month_flag=safe_int(row.get("LATEST_MONTH_FLAG"))
        )

        # Add specialty activity record
        db.session.add(specialty_activity)

    # Commit specialty records
    db.session.commit()

    print("Treatment specialty data imported successfully!")