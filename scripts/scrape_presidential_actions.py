import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# --- Configuration ---
# Base URL for scraping presidential actions.
BASE_URL = "https://www.whitehouse.gov/presidential-actions/"

# Output directory for scraped data.
OUTPUT_DIR = "data"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scrape_presidential_actions.log"),
        logging.StreamHandler()
    ]
)

def scrape_presidential_actions_page(url):
    """
    Fetches a single page of presidential actions and extracts
    the action titles and dates.
    
    Args:
        url (str): URL of the page to scrape.
    
    Returns:
        tuple: (next_url, actions)
            next_url (str or None): The URL for the next page (if available).
            actions (list): List of dictionaries with keys 'title' and 'date'.
    """
    logging.info("Fetching page URL: %s", url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error("Error fetching page: %s", e)
        return None, []

    soup = BeautifulSoup(response.text, 'lxml')
    actions = []
    
    # Locate all <li> items within the <ul> that has a class containing "wp-block-post-template"
    li_items = soup.select("ul.wp-block-post-template li")
    if not li_items:
        logging.warning("No <li> items found using selector 'ul.wp-block-post-template li' on page: %s", url)
    
    for li in li_items:
        # Find the title inside an <h2> tag with class "wp-block-post-title"
        h2 = li.find("h2", class_="wp-block-post-title")
        if not h2:
            logging.debug("No <h2> tag found in an <li> item; skipping.")
            continue
        a_tag = h2.find("a")
        if not a_tag:
            logging.debug("No <a> tag found in <h2>; skipping.")
            continue
        title = a_tag.get_text(strip=True)
        
        # Find the date inside the <div> with class "wp-block-post-date"
        date_div = li.find("div", class_="wp-block-post-date")
        date_value = None
        if date_div:
            time_tag = date_div.find("time")
            if time_tag:
                date_value = time_tag.get("datetime", time_tag.get_text(strip=True))
        
        actions.append({"title": title, "date": date_value})
    
    # Locate the "Next" pagination link using its class.
    next_link = soup.select_one("a.wp-block-query-pagination-next")
    next_url = next_link.get("href") if next_link else None
    if next_url:
        logging.info("Found next page: %s", next_url)
    else:
        logging.info("No further pages found from %s", url)
    
    return next_url, actions

def scrape_all_pages(start_url):
    """
    Iterates through all pages starting from start_url by following
    the "Next" link, and aggregates the actions from all pages.
    
    Args:
        start_url (str): The URL of the first page.
    
    Returns:
        list: A combined list of all presidential actions scraped.
    """
    all_actions = []
    current_url = start_url
    page_num = 1
    while current_url:
        logging.info("Scraping page %d: %s", page_num, current_url)
        next_url, actions = scrape_presidential_actions_page(current_url)
        all_actions.extend(actions)
        current_url = next_url
        page_num += 1
    return all_actions

def save_actions(actions):
    """
    Saves the aggregated actions into a timestamped JSON file in the OUTPUT_DIR.
    
    Args:
        actions (list): List of presidential action dictionaries.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"presidential_actions_{timestamp}.json")
    
    try:
        with open(filename, "w") as f:
            json.dump(actions, f, indent=2)
        logging.info("Data successfully saved to %s", filename)
    except IOError as e:
        logging.error("Failed to write data to file: %s", e)

if __name__ == "__main__":
    logging.info("Starting multi-page presidential actions scraping.")
    actions = scrape_all_pages(BASE_URL)
    if actions:
        save_actions(actions)
    else:
        logging.warning("No actions scraped from any pages.")
    logging.info("Scraping completed.")
