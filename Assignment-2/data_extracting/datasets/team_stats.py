import pandas as pd

def load_and_standardize(file_path, year):
    df = pd.read_csv(file_path)
    df['year'] = year
    df['Name'] = df['Name'].str.lower().str.strip()
    return df

# Load files
dfs = [
    load_and_standardize('sofifa_teams2010.csv', 2010),
    load_and_standardize('sofifa_teams2014.csv', 2014),
    load_and_standardize('sofifa_teams2018.csv', 2018),
    load_and_standardize('sofifa_teams2022.csv', 2022),
]

all_years = pd.concat(dfs, ignore_index=True)

# Save combined stacked data
all_years.to_csv('sofifa_all_years_stacked.csv', index=False)

print(f"Combined stacked dataset shape: {all_years.shape}")
