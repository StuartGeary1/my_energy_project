import os
import json
from datetime import datetime
from collections import Counter
import plotly.graph_objects as go
import plotly.io as pio

def load_data(filename):
    """Load presidential actions data from a JSON file."""
    with open(filename, "r") as f:
        return json.load(f)

def aggregate_by_hour_of_day(actions):
    """
    Aggregate presidential actions by hour of day (0 to 23), ignoring the date.
    
    For each action, extract the hour from its ISO timestamp, and count how many
    actions occurred at each hour.
    Returns a dictionary mapping hour (int) to count (int), ensuring every hour
    (0–23) is represented.
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
    # Ensure all 24 hours are included (even if count is 0)
    hourly_counts = {hour: counts.get(hour, 0) for hour in range(24)}
    return hourly_counts

def generate_polar_chart(hourly_counts):
    """
    Generate a polar bar chart (clock chart) using Plotly.
    
    Each hour is mapped to an angle (hour * 15 degrees since 360°/24 = 15°),
    and the radial value is the number of actions in that hour.
    """
    # Hours from 0 to 23
    hours = list(range(24))
    counts = [hourly_counts[h] for h in hours]
    # Map each hour to an angle (in degrees)
    theta = [h * 15 for h in hours]  # 0° for 0:00, 15° for 1:00, ..., 345° for 23:00

    fig = go.Figure(go.Barpolar(
        r = counts,
        theta = theta,
        width = [15] * 24,  # Each bar occupies 15 degrees
        marker_color = counts,
        marker_colorscale = 'Viridis',
        marker_line_color = "black",
        marker_line_width = 1,
        opacity = 0.8
    ))
    
    fig.update_layout(
        title="Aggregated Presidential Actions per Hour of Day",
        polar = dict(
            angularaxis = dict(
                direction = "clockwise",
                tickmode = "array",
                tickvals = theta,
                ticktext = [f"{h}:00" for h in hours],
                period = 360
            ),
            radialaxis = dict(
                ticksuffix = " PA",
                angle = 90,
                dtick = 1
            )
        ),
        showlegend = False
    )
    return fig

if __name__ == "__main__":
    # Update this filename as needed; here we assume a specific enriched file.
    filename = "data/presidential_actions_with_themes_20250209_222540.json"
    if not os.path.exists(filename):
        print(f"File {filename} not found!")
        exit(1)
    
    data = load_data(filename)
    print(f"Loaded {len(data)} records from {filename}.")
    
    hourly_counts = aggregate_by_hour_of_day(data)
    fig = generate_polar_chart(hourly_counts)
    
    # Open the polar chart in your default browser
    pio.show(fig)
