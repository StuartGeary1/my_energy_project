# Presidential Actions Dashboard

A Python-based data pipeline and web application that scrapes, analyzes, and visualizes presidential actions from the White House website.

## Overview

The Presidential Actions Dashboard:
- Scrapes presidential action data from the White House website
- Enriches raw data with thematic labels
- Performs quality assurance checks
- Visualizes data through multiple interactive dashboards:
  - Daily Aggregation: Bar chart showing actions per day
  - Hourly Aggregation: Polar (clock-like) chart displaying actions per hour
  - Theme Aggregation: Horizontal bar chart ranking themes by action count

All visualizations are rendered using Plotly with a dark, Amazon-inspired color scheme.

## Features

### Data Scraping
- Scrapes multiple pages from the White House Presidential Actions archive
- Stores raw data in JSON format

### Data Enrichment
- Adds theme labels based on action title keywords
- Performs quality assurance validation:
  - Date format verification
  - Non-empty title checks
  - Theme list validation

### Interactive Dashboard
- Flask web application displaying:
  - Daily aggregation chart
  - Polar chart for hourly aggregation
  - Theme ranking chart
- "Refresh Data" button to trigger real-time data updates

## Architecture

### Data Layer
- **Scraping Module**: `scripts/scrap_presidential_actions.py`
  - Fetches data from White House website
  - Saves raw JSON files to `data/` directory

### Data Processing
- **Enrichment**: `scripts/add_themes.py`
- **Quality Assurance**: `scripts/qa_data.py`

### Presentation Layer
- **Dashboard Application**: `dashboard/app.py`
  - Reads latest enriched data
  - Aggregates data for visualization
  - Renders interactive Plotly charts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/StuartGeary1/my_energy_project.git
cd my_energy_project
```

2. Create and activate virtual environment:
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Data Pipeline

1. Scrape data:
```bash
python .\scripts\scrap_presidential_actions.py
```

2. Enrich data with themes:
```bash
python .\scripts\add_themes.py
```

3. (Optional) Run QA checks:
```bash
python .\scripts\qa_data.py
```

### Running the Dashboard

1. Start Flask application:
```bash
python .\dashboard\app.py
```

2. Open browser and navigate to `http://127.0.0.1:5000/`

### Dashboard Features
- Daily Chart: Bar chart of presidential actions per day
- Hourly Chart: Polar chart showing action distribution by hour
- Theme Chart: Ranked horizontal bar chart of themes
- Refresh Data Button: Triggers real-time data updates

## Requirements

- Python 3.x
- requests==2.28.2
- beautifulsoup4==4.11.1
- lxml==4.9.2
- flask==2.2.3
- plotly==5.13.1

## Project Structure

```
MY_ENERGY_PROJECT/
├── dashboard/
│   ├── app.py               # Flask application
│   └── templates/
│       └── index.html       # Dashboard template
├── data/                    # JSON data storage
├── scripts/
│   ├── fetch_data.py        # Optional API script
│   ├── scrap_presidential_actions.py
│   ├── add_themes.py
│   └── qa_data.py
├── venv/
└── requirements.txt
```

## Deployment

- Development: Uses Flask's built-in server
- Production: Consider using:
  - WSGI server (e.g., Gunicorn)
  - Reverse proxy (e.g., Nginx)
  - Appropriate security measures

## Future Enhancements

- Database integration (e.g., SQLite)
- Automated data refresh scheduling
- Enhanced interactive features
- Cloud platform deployment

## Author

Stuart Geary  
GitHub: [StuartGeary1](https://github.com/StuartGeary1)
