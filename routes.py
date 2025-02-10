from flask import Flask, render_template, redirect, url_for, flash
import subprocess
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For flashing messages

# (Assuming DATA_DIR and load_latest_data_with_themes() are defined as above)

def aggregate_by_day(actions):
    """Aggregate article counts per day."""
    # Assuming each record has a 'date' key in ISO format; we extract the date portion.
    dates = [action["date"].split("T")[0] for action in actions if action.get("date")]
    counts = Counter(dates)
    sorted_counts = sorted(counts.items())
    return sorted_counts

def generate_chart(aggregated_data):
    """Generate a Plotly bar chart for aggregated data."""
    if not aggregated_data:
        return None
    dates, counts = zip(*aggregated_data)
    fig = go.Figure(data=[go.Bar(x=dates, y=counts)])
    fig.update_layout(
        title="Number of Presidential Actions per Day",
        xaxis_title="Date",
        yaxis_title="Number of Actions",
        template="plotly_white"
    )
    graph_json = pio.to_json(fig)
    return graph_json

@app.route("/")
def index():
    try:
        actions, source_file = load_latest_data_with_themes()
    except FileNotFoundError as e:
        flash(str(e), "danger")
        actions = []  # Fallback to empty list
        source_file = None
    aggregated_data = aggregate_by_day(actions)
    chart_json = generate_chart(aggregated_data)
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html", chart_json=chart_json, last_updated=last_updated, source_file=source_file)

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
