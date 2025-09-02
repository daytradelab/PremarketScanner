import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# Create output folder if it doesn't exist
os.makedirs("output", exist_ok=True)

# Finviz URL for premarket gappers
url = "https://finviz.com/screener.ashx?v=111&s=ta_gapup"

headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    print("Fetching data from Finviz...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract table rows
    table = soup.find("table", class_="table-light")
    rows = table.find_all("tr")[1:]  # Skip header

    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue
        ticker = cols[1].text.strip()
        price = float(cols[8].text.replace("$", "").replace(",", ""))
        volume = int(cols[9].text.replace(",", ""))
        gap = float(cols[10].text.replace("%", "").replace("+", ""))

        # Filter logic
        if price > 1 and volume > 100000 and gap > 3:
            data.append({
                "Ticker": ticker,
                "Price": price,
                "Volume": volume,
                "Gap %": gap
            })

    if data:
        df = pd.DataFrame(data)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        output_path = f"output/breakouts_{timestamp}.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df)} breakout candidates to {output_path}")
    else:
        print("No breakout candidates found.")

except Exception as e:
    print(f"Error during scan: {e}")
