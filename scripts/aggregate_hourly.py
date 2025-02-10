import json
from datetime import datetime, timedelta
from collections import Counter, OrderedDict
import plotly.graph_objs as go
import plotly.io as pio

def load_data(filename):
    """Load presidential actions data from a JSON file."""
    with open(filename, "r") as f:
        return json.load(f)

def aggregate_actions_per_hour(actions):
    """
    For each action in the list, parse the ISO timestamp and round it down to the hour.
    Then, aggregate counts for each hour in the complete range between the earliest and latest hour.
    
    Returns:
        An OrderedDict mapping datetime objects (rounded to the hour) to counts.
    """
    hours = []
    for action in actions:
        dt_str = action.get("date")
        if dt_str:
            try:
                # Parse the ISO timestamp (e.g., "2025-02-09T17:08:57-05:00")
                dt = datetime.fromisoformat(dt_str)
                # Round down to the nearest hour
                dt_hour = dt.replace(minute=0, second=0, microsecond=0)
                hours.append(dt_hour)
            except Exception as e:
                print(f"Error parsing date '{dt_str}': {e}")
    if not hours:
        return OrderedDict()
    
    # Count how many actions occurred in each hour
    counts = Counter(hours)
    
    # Determine the range of hours in the data
    min_hour = min(hours)
    max_hour = max(hours)
    
    # Create an ordered dictionary that covers every hour between min_hour and max_hour
    hourly_counts = OrderedDict()
    current_hour = min_hour
    while current_hour <= max_hour:
        hourly_counts[current_hour] = counts.get(current_hour, 0)
        current_hour += timedelta(hours=1)
    
    return hourly_counts

def generate_hourly_bar_chart(hourly_counts):
    """
    Generate a Plotly bar chart from the hourly counts.
    
    Returns:
        A Plotly Figure object.
    """
    # Format the datetime keys as strings for the x-axis
    hours_formatted = [dt.strftime("%Y-%m-%d %H:%M") for dt in hourly_counts.keys()]
    counts = list(hourly_counts.values())
    
    # Create a bar chart
    fig = go.Figure(data=[go.Bar(x=hours_formatted, y=counts)])
    fig.update_layout(
        title="Presidential Actions Per Hour",
        xaxis_title="Hour",
        yaxis_title="Count of Actions",
        xaxis_tickangle=-45,
        template="plotly_white"
    )
    return fig

if __name__ == "__main__":
    # Update the filename to your latest enriched JSON file
    filename = "data/presidential_actions_with_themes_20250209_222540.json"
    
    # Load the data from JSON
    data = load_data(filename)
    print(f"Loaded {len(data)} records from {filename}.")
    
    # Aggregate the actions per hour
    hourly_counts = aggregate_actions_per_hour(data)
    
    # Generate the hourly bar chart
    fig = generate_hourly_bar_chart(hourly_counts)
    
    # Display the chart in your default browser
    pio.show(fig)
