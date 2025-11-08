import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_fifaindex_team_data(url, year):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch {year} FIFAIndex page")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Find the table containing the team data - typically by class or id, update as per page structure
    table = soup.find("table", {"class": "table table-striped table-teams"})
    if not table:
        print(f"No table found on FIFAIndex page for {year}")
        return None

    # Parse table with pandas for convenience
    df = pd.read_html(str(table))[0]

    # Clean and add additional info
    df['year'] = year
    # Modify below per actual table headers on specific page
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]

    return df

# URLs and years from your query
urls = {
    2006: "https://www.fifaindex.com/teams/fifa06_2/?type=1",
    2014: "https://www.fifaindex.com/teams/fifa14_13/?type=1",
    2018: "https://www.fifaindex.com/teams/fifa18wc_271/",
    2022: "https://www.fifaindex.com/teams/fifa22_555/?type=1",
}

dfs = []
for year, url in urls.items():
    df = scrape_fifaindex_team_data(url, year)
    if df is not None:
        dfs.append(df)

# Combine all years into one dataframe
combined_df = pd.concat(dfs, ignore_index=True)

# Save combined dataset
combined_df.to_csv("combined_fifaindex_teams.csv", index=False)
print("Saved combined FIFAIndex team data for years 2006, 2014, 2018, 2022.")
