import pandas as pd

# Load cleaned tables that contain team data (adjust file names after your cleaning process)
team_records = pd.read_csv("wiki_table_4_cleaned.csv")  # Overall team records
medal_table = pd.read_csv("wiki_table_7_cleaned.csv")    # Medal counts
appearances = pd.read_csv("wiki_table_9_cleaned.csv")    # Appearances, qualifier data, etc.

# Preview column names for alignment
print(team_records.columns)
print(medal_table.columns)
print(appearances.columns)

# Standardize team/country name column - assuming 'team' or 'nation' column
# Standardize merge key for all tables
for df in [team_records, medal_table, appearances]:
    if 'nation' in df.columns:
        df.rename(columns={'nation': 'team'}, inplace=True)
    if 'team(s)' in df.columns:
        df.rename(columns={'team(s)': 'team'}, inplace=True)
    if 'team' in df.columns:
        df['team'] = df['team'].str.lower().str.strip()


# Rename columns if needed for merging keys
medal_table.rename(columns={'nation': 'team'}, inplace=True)
appearances.rename(columns={'nation': 'team'}, inplace=True)

# Merge datasets stepwise
merged_df = pd.merge(team_records, medal_table, on='team', how='outer')
merged_df = pd.merge(merged_df, appearances, on='team', how='outer')

# Clean merged data further (handle NAs, type conversion)
merged_df.fillna(0, inplace=True)
merged_df.reset_index(drop=True, inplace=True)

# Save combined table
merged_df.to_csv("wiki_combined_team_data.csv", index=False)
print("Saved combined team data csv with shape:", merged_df.shape)
print(merged_df.head())
