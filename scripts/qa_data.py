import os
import json
from datetime import datetime
from collections import defaultdict, Counter

def load_data(filename):
    """Load JSON data from a file."""
    with open(filename, "r") as f:
        return json.load(f)

def validate_record(record, index):
    """Perform QA checks on one record.
    
    Returns a list of error messages (empty if no errors).
    """
    errors = []
    # Check title exists and is non-empty.
    title = record.get("title")
    if not title or not title.strip():
        errors.append("Missing or empty title")
    
    # Check date exists and is a valid ISO datetime.
    date_str = record.get("date")
    if not date_str:
        errors.append("Missing date")
    else:
        try:
            datetime.fromisoformat(date_str)
        except Exception as e:
            errors.append(f"Invalid date format: {date_str}")
    
    # Check themes field exists, is a list, and is non-empty.
    themes = record.get("themes")
    if themes is None:
        errors.append("Missing 'themes' field")
    elif not isinstance(themes, list) or not themes:
        errors.append("Empty or invalid 'themes' field")
    
    return errors

def validate_data(data):
    """
    Validate all records in the data.
    
    Returns:
      - errors: a list of tuples (index, record, error_list)
      - duplicates: a dictionary mapping (title, date) keys to list of indices (if duplicates exist)
      - valid_data: the list of records (this may be the same as data if no errors are fixed)
    """
    errors = []
    duplicates = defaultdict(list)
    seen = {}
    
    for idx, record in enumerate(data):
        rec_errors = validate_record(record, idx)
        if rec_errors:
            errors.append((idx, record, rec_errors))
        
        key = (record.get("title"), record.get("date"))
        if key in seen:
            duplicates[key].append(idx)
        else:
            seen[key] = idx
    
    return errors, duplicates, data

def fix_data(data):
    """
    Apply fixes to the data.
    
    For example, if a record has a missing or empty themes field, set it to a default theme.
    """
    default_theme = ["America First"]
    for record in data:
        themes = record.get("themes")
        if themes is None or (isinstance(themes, list) and not themes):
            record["themes"] = default_theme
    return data

def print_qa_summary(errors, duplicates, total_records):
    """Print a summary report of QA findings."""
    print("QA Summary:")
    print(f"Total records: {total_records}")
    print(f"Records with errors: {len(errors)}")
    if errors:
        for idx, rec, err_list in errors:
            title = rec.get("title", "<no title>")
            print(f"Record {idx} ('{title}'): ")
            for err in err_list:
                print(f"  - {err}")
    else:
        print("No individual record errors found.")
    
    dup_count = sum(len(idxs)-1 for idxs in duplicates.values() if len(idxs) > 1)
    if dup_count:
        print(f"Found {dup_count} duplicate records:")
        for key, idxs in duplicates.items():
            if len(idxs) > 1:
                print(f"  Duplicate key {key}: indices {idxs}")
    else:
        print("No duplicate records found.")

def main():
    # Update this filename as needed.
    input_filename = "data/presidential_actions_with_themes_20250209_222540.json"
    
    if not os.path.exists(input_filename):
        print(f"Error: File {input_filename} not found.")
        return

    data = load_data(input_filename)
    total_records = len(data)
    errors, duplicates, _ = validate_data(data)
    print_qa_summary(errors, duplicates, total_records)
    
    # If errors were found (or if you wish to force a fix), apply fixes.
    if errors:
        print("\nApplying fixes to records with issues (e.g., adding default theme if missing)...")
        fixed_data = fix_data(data)
    else:
        fixed_data = data  # No changes needed

    # Save the fixed data to a new file for updating your database
    output_filename = os.path.join("data", f"presidential_actions_with_themes_qa_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_filename, "w") as f:
        json.dump(fixed_data, f, indent=2)
    
    print(f"\nFixed data saved to {output_filename}")

if __name__ == "__main__":
    main()
