import requests
import pandas as pd
from bs4 import BeautifulSoup

# Wikipedia URL
wiki_url = "https://en.wikipedia.org/wiki/FIFA_World_Cup_records_and_statistics"

# Use custom headers to bypass 403
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0 Safari/537.36"
}

# Get page content
response = requests.get(wiki_url, headers=headers)

if response.status_code == 200:
    print("Page fetched successfully")
    soup = BeautifulSoup(response.text, "html.parser")
else:
    raise Exception(f"Failed to retrieve page: {response.status_code}")

# Extract all tables as HTML and read via pandas
tables = pd.read_html(str(soup))
print(f"Found {len(tables)} tables")

# Cleaning function
def clean_table(df):
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df = df.dropna(how="all")
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(r"\[.*?\]", "", regex=True).str.strip()
    return df

# Clean and Save all tables
for i, t in enumerate(tables):
    cleaned = clean_table(t)
    filename = f"wiki_table_{i+1}_cleaned.csv"
    cleaned.to_csv(filename, index=False)
    print(f"Saved {filename} with {cleaned.shape[0]} rows and {cleaned.shape[1]} columns")

print("Wikipedia scraping completed successfully!")
