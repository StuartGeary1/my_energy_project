import os
import json
import requests
from datetime import datetime
import logging

# --- Configuration ---
# Update these values with your actual API details.
API_URL = "https://www.whitehouse.gov/presidential-actions/"  # Replace with your actual API endpoint.
API_KEY = "YOUR_API_KEY"  # If an API key is needed, otherwise remove from params.
# Additional parameters if needed (modify or extend as necessary)
PARAMS = {
    "api_key": API_KEY,
    "format": "json"
}

# Output directory for raw data
OUTPUT_DIR = "data"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("fetch_data.log"),
        logging.StreamHandler()
    ]
)

def fetch_data():
    """
    Makes an API GET request to the configured API endpoint,
    handles errors, and writes the JSON response to a file.
    """
    try:
        logging.info("Sending request to API: %s", API_URL)
        response = requests.get(API_URL, params=PARAMS, timeout=10)  # timeout to avoid hangs
        response.raise_for_status()  # Raises HTTPError if response code is not 200
    except requests.RequestException as e:
        logging.error("API request failed: %s", e)
        return

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON: %s", e)
        return

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"api_data_{timestamp}.json")
    
    try:
        with open(filename, "w") as outfile:
            json.dump(data, outfile, indent=2)
        logging.info("Data successfully saved to %s", filename)
    except IOError as e:
        logging.error("Failed to write data to file: %s", e)

if __name__ == "__main__":
    fetch_data()
