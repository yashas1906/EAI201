import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_fifa_rankings(year_start=2002, year_end=2022):
    all_data = []
    base_url = "https://www.fifa.com/fifa-world-ranking/ranking-table/men/rank/id{}"
    # FIFA ID for ranking snapshots: simulate by year suffix (example purposes)

    for year in range(year_start, year_end + 1):
        # For each year, find the ranking snapshot. This site may not provide direct per-year URL,
        # so scraping latest or specific monthly snapshots might be needed.
        # This is an example, adjust with correct URL or API to get yearly ranking.
        # Here we simulate by accessing December snapshot
        print(f"Fetching data for year {year}...")
        url = f"https://www.fifa.com/fifa-world-ranking/men?date={year}-12-31"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for ranking table by inspecting site structure
        table = soup.find('table')  # Adjust selector as per actual site structure
        if table is None:
            print(f"No table found for year {year}")
            continue

        headers = [th.text.strip() for th in table.find_all('th')]
        rows = []
        for tr in table.find_all('tr')[1:]:
            cols = [td.text.strip() for td in tr.find_all('td')]
            if len(cols) == len(headers):
                rows.append(cols)

        df_year = pd.DataFrame(rows, columns=headers)
        df_year['Year'] = year
        all_data.append(df_year)

    combined_df = pd.concat(all_data, ignore_index=True)

    # Normalize columns and data types as needed
    print("Saving combined FIFA rankings CSV")
    combined_df.to_csv('fifa_rankings_2002_2022.csv', index=False)

if __name__ == "__main__":
    scrape_fifa_rankings()
