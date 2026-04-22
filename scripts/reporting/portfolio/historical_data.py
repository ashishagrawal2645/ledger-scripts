"""NSE NIFTY 50 historical close prices. Fetches and appends to CSV with resume support."""

import os
import csv
import requests
import json
import time
from datetime import datetime, timedelta

DATE_FMT = "%d-%m-%Y"
NSE_ORIGIN = "https://www.nseindia.com"
API_URL = "https://www.nseindia.com/api/historicalOR/indicesHistory"
DEFAULT_START_DATE = "01-04-2024"
BATCH_DAYS = 60
CSV_PATH = os.path.join(os.path.dirname(__file__), "nifty_historical_prices.csv")


def _parse_nse_date(date_str):
    """Parse NSE date (e.g. 15-Jan-2026) or DD-MM-YYYY. Returns datetime or None."""
    for fmt in ("%d-%b-%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def get_last_date_from_csv():
    """Return the last date present in the CSV, or None if empty/missing."""
    if not os.path.exists(CSV_PATH):
        return None
    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return None
            last_row = None
            for row in reader:
                if len(row) >= 2 and row[0].strip():
                    last_row = row
            if not last_row:
                return None
            return _parse_nse_date(last_row[0])
    except (OSError, csv.Error):
        return None


def fetch_nifty50_close_prices(start_date_str, end_date_str, print_results=True):
    """
    Fetches NIFTY 50 day-end closing prices from NSE India in 60-day batches.

    Args:
        start_date_str (str): Start date in 'DD-MM-YYYY' format
        end_date_str (str): End date in 'DD-MM-YYYY' format
        print_results (bool): Whether to print progress (default: True)

    Returns:
        list: List of tuples (date_str, close_price) or empty list on error
    """
    try:
        start_date = datetime.strptime(start_date_str, DATE_FMT)
        end_date = datetime.strptime(end_date_str, DATE_FMT)
    except ValueError:
        if print_results:
            print("Error: Please provide dates in DD-MM-YYYY format.")
        return []

    if start_date > end_date:
        if print_results:
            print("Error: Start date must be earlier than the end date.")
        return []

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Referer": f"{NSE_ORIGIN}/",
    })

    if print_results:
        print("Establishing session with NSE...")
    try:
        session.get(NSE_ORIGIN, timeout=10)
    except requests.exceptions.RequestException as e:
        if print_results:
            print(f"Failed to connect to NSE: {e}")
        return []

    all_prices = []
    chunk_start = start_date

    while chunk_start <= end_date:
        chunk_end = min(chunk_start + timedelta(days=BATCH_DAYS - 1), end_date)
        c_start_str = chunk_start.strftime(DATE_FMT)
        c_end_str = chunk_end.strftime(DATE_FMT)

        if print_results:
            print(f"Fetching data from {c_start_str} to {c_end_str}...")

        url = f"{API_URL}?indexType=NIFTY%2050&from={c_start_str}&to={c_end_str}"
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            json_data = response.json()
            if "data" in json_data and isinstance(json_data["data"], list):
                for record in json_data["data"]:
                    date_str = record.get("EOD_TIMESTAMP", "")
                    close_price = record.get("EOD_CLOSE_INDEX_VAL", "")
                    if date_str and close_price:
                        all_prices.append((date_str, str(close_price)))
            else:
                if print_results:
                    print("Warning: Unexpected JSON structure in response.")
        except requests.exceptions.RequestException as e:
            if print_results:
                print(f"Error fetching data for chunk {c_start_str} - {c_end_str}: {e}")
        except json.JSONDecodeError as e:
            if print_results:
                print(f"Error parsing JSON for chunk {c_start_str} - {c_end_str}: {e}")

        chunk_start = chunk_end + timedelta(days=1)
        time.sleep(1.5)

    return all_prices


def update_csv(print_results=True):
    """
    Fetch NIFTY 50 prices from 01-Apr-2024 to yesterday (or from last CSV date).
    Appends new rows to nifty_historical_prices.csv.
    """
    end_date = datetime.now().date() - timedelta(days=1)
    end_str = end_date.strftime(DATE_FMT)

    last = get_last_date_from_csv()
    if last is not None:
        # last is datetime; next fetch starts the day after
        start_dt = last + timedelta(days=1)
        start_str = start_dt.strftime(DATE_FMT)
        if print_results:
            print(f"Resuming from last CSV date: fetching {start_str} to {end_str}")
    else:
        start_str = DEFAULT_START_DATE
        if print_results:
            print(f"Fetching from {start_str} to {end_str}")

    start_dt = datetime.strptime(start_str, DATE_FMT)
    end_dt = datetime.strptime(end_str, DATE_FMT)
    if start_dt > end_dt:
        if print_results:
            print("CSV is already up to date (through yesterday).")
        return

    new_prices = fetch_nifty50_close_prices(start_str, end_str, print_results=print_results)
    if not new_prices:
        if print_results:
            print("No new data to write.")
        return

    # Sort by date ascending (NSE returns newest-first)
    def sort_key(row):
        dt = _parse_nse_date(row[0])
        return dt if dt is not None else datetime.max

    new_prices.sort(key=sort_key)

    file_exists = os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "close_price"])
        for date_val, close_val in new_prices:
            writer.writerow([date_val, close_val])

    if print_results:
        print(f"Wrote {len(new_prices)} rows to {os.path.basename(CSV_PATH)}.")


if __name__ == "__main__":
    update_csv()
