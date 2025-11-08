import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# List of FIFA World Cup years (each tournament)
seasons = [2002, 2006, 2010, 2014, 2018, 2022]
base_url = "https://www.espn.in/football/stats/_/league/FIFA.WORLD/season/{}/view/discipline"

all_data = []

for season in seasons:
    print(f"Scraping ESPN season {season} discipline stats...")
    url = base_url.format(season)
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table")
    if not table:
        print(f"No table found for {season}")
        continue

    headers = [h.text.strip() for h in table.find_all("th")]
    data = []
    for row in table.find_all("tr")[1:]:
        cols = [td.text.strip() for td in row.find_all("td")]
        if len(cols) == len(headers):
            data.append(cols)

    if data:
        df = pd.DataFrame(data, columns=headers)
        df["Season"] = season
        all_data.append(df)
    
    time.sleep(2)

# Combine all data
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)

    # Normalize column names using flexible mapping
    rename_map = {
        'RK': 'Rank',
        'TEAM': 'Team',
        'P': 'Games Played',
        'YC': 'Yellow Cards',
        'RC': 'Red Cards',
        'PTS': 'Points'
    }
    combined_df.rename(columns=rename_map, inplace=True)

    # Convert numeric columns safely
    for col in ['Rank', 'Games Played', 'Yellow Cards', 'Red Cards', 'Points']:
        if col in combined_df.columns:
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

    combined_df.to_csv('espn_fifa_discipline_2002_2022.csv', index=False)
    print("Saved ESPN discipline dataset to espn_fifa_discipline_2002_2022.csv")

else:
    print("No season data found.")
