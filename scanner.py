import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

print("scanner.py started")  # Confirm script is executing

def fetch_finviz_data():
    print("Fetching Finviz HTML...")
    url = "https://finviz.com/screener.ashx?v=111&s=ta_gapup"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch Finviz data: {response.status_code}")
    return response.content

def parse_table(html):
    print("Parsing HTML content...")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="table-light")
    if not table:
        raise ValueError("Finviz table not found")
    rows = table.find_all("tr")[1:]  # Skip header
    print(f"Found {len(rows)} rows in table")
    return rows

def extract_candidates(rows):
    print("Extracting breakout candidates...")
    candidates = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 11:
            continue
        try:
            ticker = cols[1].text.strip()
            price = float(cols[8].text.replace("$", "").replace(",", ""))
            volume = int(cols[9].text.replace(",", ""))
            gap = float(cols[10].text.replace("%", "").replace("+", ""))
            if price > 1 and volume > 100_000 and gap > 3:
                candidates.append({
                    "Ticker": ticker,
                    "Price": price,
                    "Volume": volume,
                    "Gap %": gap
                })
        except Exception as e:
            print(f"Skipping row due to error: {e}")
    print(f"Extracted {len(candidates)} valid breakout candidates")
    return candidates

def save_to_csv(data):
    print("Saving results to CSV...")
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path = f"output/breakouts_{timestamp}.csv"
    pd.DataFrame(data).to_csv(path, index=False)
    print(f"Saved {len(data)} breakout candidates to {path}")

def main():
    print("Starting breakout scan...")
    try:
        html = fetch_finviz_data()
        rows = parse_table(html)
        candidates = extract_candidates(rows)
        if candidates:
            save_to_csv(candidates)
            exit(0)
        else:
            print("No breakout candidates found.")
            exit(20)
    except Exception as e:
        print(f"Unhandled error: {e}")
        exit(2)

if __name__ == "__main__":
    main()


