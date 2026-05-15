## Project Overview
The NHS Hospital Activity Explorer is a Flask-based web application that analyses NHS Hospital Episode Statistics (HES) open data from England. The system allows users to explore provider activity, compare NHS organisations, and analyse healthcare trends using admissions, outpatient attendance, emergency activity, and missed appointment data.

## Features

### Provider Explorer:
- Browse NHS providers with pagination
- Search providers by organisation name
- Filter providers by:
  - Region
  - Minimum admissions
  - Outpatient activity
- View detailed provider analytics pages

### Provider Detail Analytics
- Total admissions summary
- Outpatient attendance totals
- Missed appointment (DNA) rates
- Regional provider ranking
- National average comparisons
- Monthly activity breakdown

### Analytics Dashboard
- Best-performing providers
- Worst-performing providers
- Regional emergency admission analysis
- Provider performance scoring
- Admissions versus missed appointment correlation
- Highest outpatient attendance providers
- Treatment specialty workload analysis

### Age-Based Analytics
- Highest-risk age groups
- Emergency activity by age band
- Missed appointment rates by age group
- Best and worst performing age bands

### Provider Comparison
- Compare two or three NHS providers side-by-side
- Analyse admissions, outpatient attendance, and emergency activity
- Validate duplicate provider selections

### Additional Features
- Custom 404 and 500 error pages
- Responsive design for mobile and tablet devices
- Automated tests using pytest
- Render cloud deployment

## Technologies Used
- Python
- Flask
- SQLAlchemy
- SQLite
- HTML/CSS
- Jinja2
- Pandas
- Pytest
- Gunicorn
- Render

## Dataset Information
The application uses NHS Hospital Episode Statistics (HES) open data from England.

### Datasets include:
- Provider-level hospital activity
- Age-band healthcare activity
- Treatment specialty activity

### Metrics analysed include:
- Emergency admissions
- Elective admissions
- Outpatient attendance
- Missed appointments (DNA)
- Emergency demand trends

The imported dataset was limited to a suitable coursework-sized subset while preserving realistic NHS analytics and relational database functionality.


## Project Structure
The project is organised as follows:

- nhs-hospital-activity/: Main Flask application project
- app/: Core application containing routes, models, services, templates, and static files
- app/templates/: HTML templates rendered using Jinja2
- app/static/: CSS styling and static assets
- scripts/: Data-loading and Database-creation scripts for NHS CSV datasets
- tests/: Automated pytest test suite
- requirements.txt: Python project dependencies
- wsgi.py: WSGI entry point for Render deployment
- README.md: Project documentation



## Installation

1. Clone Repository

```bash
git clone https://github.com/52533734/nhs-hospital-activity.git
cd nhs-hospital-activity
```

2. Create Virtual Environment

```bash
python -m venv venv
```
3. Activate Virtual Environment
Windows
```bash
venv\Scripts\activate
```
Mac/Linux
```bash
source venv/bin/activate
```

4. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

1. Create Database
```bash
python scripts/create_db.py
```

2. Load NHS Data
```bash
python scripts/load_data.py
```

3. Start Flask Server
```bash
flask run
```

4. Open in Browser
```bash
http://127.0.0.1:5000
```

## Testing
Run all automated tests:
```bash
pytest
```
The project includes 41 automated tests covering:
- Model Tests
- Route Tests
- Service-layer analytics tests
- Validation tests
- Error handling test

## Deployment
The application is deployed using Render.

### Live Application
https://nhs-hospital-activity.onrender.com

### Render Configuration
Build command:
```bash
pip install -r requirements.txt && python scripts/create_db.py && python scripts/load_data.py
```

Start command:
```bash
gunicorn wsgi:app
```

## Git Workflow
The project was developed using Git and GitHub with:
- Feature branches
- Merge commits
- Incremental developmental commits
- Version tracking
- Deployment commits

## Acknowledgements
This project uses NHS Hospital Episode Statistics (HES) open datasets published by NHS England.
