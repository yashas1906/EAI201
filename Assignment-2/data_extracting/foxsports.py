import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_foxsports(seasons=[2002, 2006, 2010, 2014, 2018, 2022]):
    base_url_template = "https://www.foxsports.com/soccer/{year}-fifa-world-cup/stats"
    all_data = []

    for year in seasons:
        print(f"Scraping FoxSports World Cup stats for {year} ...")
        url = base_url_template.format(year=year)
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find('table')
        if not table:
            print(f"No table found for {year}")
            continue

        headers = [th.text.strip() for th in table.find_all('th')]
        rows = []
        for row in table.find_all('tr')[1:]:
            cols = [td.text.strip() for td in row.find_all('td')]
            if len(cols) == len(headers):
                rows.append(cols)

        df_year = pd.DataFrame(rows, columns=headers)
        df_year['Year'] = year
        all_data.append(df_year)
        time.sleep(2)  # delay to be polite

    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.to_csv("foxsports_fifa_wc_stats_2002_2022.csv", index=False)
    print("Saved FoxSports FIFA World Cup stats to foxsports_fifa_wc_stats_2002_2022.csv")

if __name__ == "__main__":
    scrape_foxsports()
