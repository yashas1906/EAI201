import pandas as pd

# Load existing FIFA overall dataset
fifa_overall_df = pd.read_csv('fifa_data.csv', encoding='latin1')
fifa_overall_df['Team'] = fifa_overall_df['Team'].str.strip().str.title()

# Load discipline data
discipline_df = pd.read_excel('espn_discipline_2010_2022.xlsx')
discipline_df['Team'] = discipline_df['Team'].str.strip().str.title()

# Make sure 'year' column present, rename if needed
if 'Season' in discipline_df.columns:
    discipline_df.rename(columns={'Season': 'year'}, inplace=True)

# Pivot discipline data so each stat per year becomes column
# Example of columns to pivot (adjust as per your file)
pivot_columns = ['yc', 'rc', 'Points']  # yellow cards, red cards, points for example
pivot_df = discipline_df.pivot(index='Team', columns='year', values=pivot_columns)

# Flatten multi-level columns to single level with year suffix
pivot_df.columns = [f'{col}_{year}' for col, year in pivot_df.columns]

# Reset index to get Team as column
pivot_df.reset_index(inplace=True)

# Merge pivoted discipline data into FIFA overall by Team
merged_df = pd.merge(fifa_overall_df, pivot_df, on='Team', how='left')

# Save result
merged_df.to_csv('fifa_overall_with_discipline_features.csv', index=False)
print("Merged FIFA overall with yearly discipline features saved.")
