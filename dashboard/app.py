import os
import json
import subprocess
from datetime import datetime
from collections import Counter, defaultdict
from flask import Flask, render_template, redirect, url_for, flash
import plotly.graph_objs as go
import plotly.io as pio

# Explicitly define the templates folder.
app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "dashboard", "templates"))
app.secret_key = "your_secret_key"  # Replace with a secure key

DATA_DIR = os.path.join(os.getcwd(), "data")

def load_latest_data_with_themes():
    """
    Load the most recent JSON file with themes from the DATA_DIR.
    Looks for files starting with "presidential_actions_with_themes_".
    """
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("presidential_actions_with_themes_") and f.endswith(".json")]
    if not files:
        raise FileNotFoundError("No updated data file with themes found in the data directory.")
    files.sort(key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)), reverse=True)
    latest_file = os.path.join(DATA_DIR, files[0])
    with open(latest_file, "r") as f:
        data = json.load(f)
    return data, latest_file

def aggregate_by_day(actions):
    """
    Aggregate the number of actions per day.
    Assumes each action has a 'date' key in ISO format.
    """
    dates = [action["date"].split("T")[0] for action in actions if action.get("date")]
    counts = Counter(dates)
    sorted_counts = sorted(counts.items())
    return sorted_counts

def aggregate_by_hour_of_day(actions):
    """
    Aggregate presidential actions by hour of day (0 to 23), ignoring the date.
    Returns a dictionary mapping hour (int) to count (int) for all 24 hours.
    """
    hours = []
    for action in actions:
        dt_str = action.get("date")
        if dt_str:
            try:
                dt = datetime.fromisoformat(dt_str)
                hours.append(dt.hour)
            except Exception as e:
                print(f"Error parsing date '{dt_str}': {e}")
    counts = Counter(hours)
    hourly_counts = {hour: counts.get(hour, 0) for hour in range(24)}
    return hourly_counts

def aggregate_by_theme(actions):
    """
    Aggregate counts for each theme across all actions.
    Each record's 'themes' is a list; count each theme.
    Returns a sorted list of tuples (theme, count) in descending order.
    """
    theme_counter = Counter()
    for action in actions:
        themes = action.get("themes", [])
        for theme in themes:
            theme_counter[theme] += 1
    sorted_themes = sorted(theme_counter.items(), key=lambda x: x[1], reverse=True)
    return sorted_themes

def generate_daily_chart(aggregated_data):
    """
    Generate a standard bar chart for daily aggregated data using a dark theme.
    """
    if not aggregated_data:
        return None
    dates, counts = zip(*aggregated_data)
    fig = go.Figure(data=[go.Bar(x=dates, y=counts, marker_color='#00704A')])  # Amazon Green
    fig.update_layout(
        title="Number of Presidential Actions per Day",
        xaxis_title="Date",
        yaxis_title="Number of Actions",
        template="plotly_dark"
    )
    return pio.to_json(fig)

def generate_polar_chart(hourly_counts):
    """
    Generate a polar (clock-like) bar chart for hourly aggregated data using a dark theme.
    Each hour is mapped to an angle (hour * 15°) and the radial length is the count.
    """
    hours = list(range(24))
    counts = [hourly_counts[h] for h in hours]
    theta = [h * 15 for h in hours]  # 0° for 0:00, 15° for 1:00, …, 345° for 23:00

    fig = go.Figure(go.Barpolar(
        r=counts,
        theta=theta,
        width=[15]*24,
        marker_color=counts,
        marker_colorscale='Portland',  # A striking, dark colorscale
        marker_line_color="white",
        marker_line_width=1,
        opacity=0.8
    ))
    fig.update_layout(
        title="Aggregated Presidential Actions per Hour of Day",
        polar=dict(
            angularaxis=dict(
                direction="clockwise",
                tickmode="array",
                tickvals=theta,
                ticktext=[f"{h}:00" for h in hours],
                period=360,
                color='white'
            ),
            radialaxis=dict(
                ticksuffix=" PA",
                dtick=1,
                color='white'
            )
        ),
        showlegend=False,
        template="plotly_dark"
    )
    return pio.to_json(fig)

def generate_theme_chart(aggregated_theme_data):
    """
    Generate a horizontal bar chart for theme counts, sorted in descending order.
    """
    if not aggregated_theme_data:
        return None
    themes, counts = zip(*aggregated_theme_data)
    # Reverse the order for horizontal bars (highest on top)
    themes = list(themes)[::-1]
    counts = list(counts)[::-1]
    fig = go.Figure(data=[go.Bar(
        x=counts,
        y=themes,
        orientation='h',
        marker_color='#FF9900'  # Amazon Orange
    )])
    fig.update_layout(
        title="Presidential Actions by Theme",
        xaxis_title="Count of Actions",
        yaxis_title="Theme",
        template="plotly_dark"
    )
    return pio.to_json(fig)

@app.route("/")
def index():
    try:
        actions, source_file = load_latest_data_with_themes()
    except FileNotFoundError as e:
        flash(str(e), "danger")
        actions = []
        source_file = None

    aggregated_daily = aggregate_by_day(actions)
    daily_chart_json = generate_daily_chart(aggregated_daily)

    aggregated_hourly = aggregate_by_hour_of_day(actions)
    polar_chart_json = generate_polar_chart(aggregated_hourly)

    aggregated_theme = aggregate_by_theme(actions)
    theme_chart_json = generate_theme_chart(aggregated_theme)

    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html",
                           daily_chart_json=daily_chart_json,
                           polar_chart_json=polar_chart_json,
                           theme_chart_json=theme_chart_json,
                           last_updated=last_updated,
                           source_file=source_file)

@app.route("/refresh")
def refresh():
    """Trigger the scraping script to update data."""
    try:
        result = subprocess.run(
            ["python", os.path.join("scripts", "scrap_presidential_actions.py")],
            capture_output=True,
            text=True,
            check=True
        )
        flash("Data refresh initiated successfully.", "success")
    except subprocess.CalledProcessError as e:
        flash(f"Data refresh failed: {e.stderr}", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
