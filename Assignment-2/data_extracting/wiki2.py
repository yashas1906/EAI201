import pandas as pd
import requests

url = "https://en.wikipedia.org/wiki/FIFA_Club_World_Cup_records_and_statistics"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

response = requests.get(url, headers=headers)
response.raise_for_status()
tables = pd.read_html(response.text)

performance_by_nation = None

for i, table in enumerate(tables):
    if 'Nation' in table.columns:
        performance_by_nation = table
        print(f"Found 'Performance by nation' table at index {i}")
        break

if performance_by_nation is not None:
    performance_by_nation.columns = [col.lower().replace(' ', '_') for col in performance_by_nation.columns]
    performance_by_nation.to_csv("fifa_club_wc_performance_by_nation.csv", index=False)
    print("Table saved as 'fifa_club_wc_performance_by_nation.csv'")
    print(performance_by_nation.head())
else:
    print("Performance by nation table not found.")
