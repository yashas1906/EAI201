import pandas as pd

def scrape_and_merge_fifa_rankings():
    # URLs for FIFA ranking snapshots for the desired years
    urls = {
        2002: "https://en.fifaranking.net/ranking/?d=2002-05-15",
        2006: "https://en.fifaranking.net/ranking/?d=2006-05-17",
        2010: "https://en.fifaranking.net/ranking/?d=2010-12-15",
        2014: "https://en.fifaranking.net/ranking/?d=2014-07-17",
        2018: "https://en.fifaranking.net/ranking/?d=2018-07-19",
        2022: "https://en.fifaranking.net/ranking/?d=2022-12-22",
    }

    all_dfs = []

    for year, url in urls.items():
        print(f"Scraping top 100 FIFA teams for {year}...")
        tables = pd.read_html(url)
        ranking = tables[0].head(100)  # First table on page; top 100 only
        ranking['year'] = year
        all_dfs.append(ranking)

    # Combine all years into a single dataframe
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Standardize column names
    combined_df.columns = [col.lower().replace(' ', '_') for col in combined_df.columns]

    # Save combined CSV
    combined_df.to_csv('fifa_top100_2002_2022.csv', index=False)
    print("Saved combined top 100 FIFA rankings as 'fifa_top100_2002_2022.csv'.")

if __name__ == "__main__":
    scrape_and_merge_fifa_rankings()
