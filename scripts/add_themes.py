import os
import json
from datetime import datetime

def get_themes(title):
    """
    Analyze the title (case-insensitive) and return a list of matching themes.
    If no specific keywords are detected, default to 'America First'.
    """
    themes = set()
    lower_title = title.lower()
    
    # National Security & Border Enforcement
    if any(keyword in lower_title for keyword in [
        "border", "security", "terrorist", "invasion", "guantanamo", 
        "sanctions", "emergency", "military", "defending", "protection",
        "northern border", "southern border", "aviation", "fighting force",
        "readiness", "iron dome", "counterterror"
    ]):
        themes.add("National Security & Border Enforcement")
    
    # Cultural & Traditional Values
    if any(keyword in lower_title for keyword in [
        "second amendment", "faith", "anti-christian", "traditional", "cultural", 
        "pardon", "clemency", "restoring", "declassification", "anti-semitism", 
        "gender ideology", "indecency", "inauguration", "children", "educational freedom",
        "ending radical", "reinstating"
    ]):
        themes.add("Cultural & Traditional Values")
    
    # Deregulation & Economic Nationalism
    if any(keyword in lower_title for keyword in [
        "deregulation", "prosperity", "sovereign wealth", "trade policy", 
        "economic", "budget", "jobs", "free market", "expanding", "unleashing"
    ]):
        themes.add("Deregulation & Economic Nationalism")
    
    # Foreign Policy Realignment
    if any(keyword in lower_title for keyword in [
        "withdrawing", "united nations", "international", "foreign", "diplomatic", 
        "oecd", "global", "foreign aid", "south africa", "china", "revising", 
        "sanctions", "withdraw", "extradition"
    ]):
        themes.add("Foreign Policy Realignment")
    
    # Celebratory & Identity-Driven Initiatives
    if any(keyword in lower_title for keyword in [
        "day", "month", "celebrating", "anniversary", "remembrance", "birthday", 
        "commemorating", "golden age", "250th", "flag"
    ]):
        themes.add("Celebratory & Identity-Driven Initiatives")
    
    # Default if no theme is found
    if not themes:
        themes.add("America First")
    
    return list(themes)

def add_themes_to_data(raw_data):
    """
    For each record in the raw data (list of dicts), add a new 'themes' key with a list of theme labels.
    """
    for record in raw_data:
        title = record.get("title", "")
        record["themes"] = get_themes(title)
    return raw_data

def load_latest_json(data_dir, prefix="presidential_actions_", suffix=".json"):
    """
    Locate the most recent JSON file in the given directory that matches the naming pattern.
    Returns the loaded data and the filename.
    """
    files = [f for f in os.listdir(data_dir) if f.startswith(prefix) and f.endswith(suffix)]
    if not files:
        raise FileNotFoundError("No matching data files found in the directory.")
    # Sort files by modification time (latest first)
    files.sort(key=lambda f: os.path.getmtime(os.path.join(data_dir, f)), reverse=True)
    latest_file = os.path.join(data_dir, files[0])
    with open(latest_file, "r") as f:
        data = json.load(f)
    return data, latest_file

def save_updated_data(data, data_dir):
    """
    Saves the updated data (with themes) into a new JSON file in the data directory,
    using a timestamped filename.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = os.path.join(data_dir, f"presidential_actions_with_themes_{timestamp}.json")
    with open(new_filename, "w") as f:
        json.dump(data, f, indent=2)
    return new_filename

if __name__ == "__main__":
    DATA_DIR = "data"
    try:
        raw_data, latest_file = load_latest_json(DATA_DIR)
        print(f"Loaded data from {latest_file} ({len(raw_data)} records).")
    except FileNotFoundError as e:
        print(e)
        exit(1)
    
    updated_data = add_themes_to_data(raw_data)
    output_file = save_updated_data(updated_data, DATA_DIR)
    print(f"Updated data with themes saved to {output_file}")
