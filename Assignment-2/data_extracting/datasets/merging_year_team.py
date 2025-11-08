import pandas as pd

# 1. Load the primary overall stats file
overall = pd.read_csv('fifa_overallstats.csv', encoding='latin1')
overall['team_clean'] = overall['Team'].str.lower().str.strip()

# 2. Prepare the primary team order from overall stats
primary_order = overall['team_clean'].tolist()

# 3. Load and clean the Sofifa yearly stats
sofifa = pd.read_csv('sofifa_all_years_stacked.csv', encoding='latin1')
sofifa['team_clean'] = sofifa['Team'].str.lower().str.strip()

# 4. Pivot Sofifa data into wide format per team
sofifa_stat_cols = [c for c in sofifa.columns if c not in ['Team', 'year', 'team_clean']]
sofifa_pivot = sofifa.pivot(index='team_clean', columns='year', values=sofifa_stat_cols)
sofifa_pivot.columns = [f'{stat}_{yr}' for stat, yr in sofifa_pivot.columns]
sofifa_pivot.reset_index(inplace=True)

# 5. Merge Sofifa pivoted data as extra columns into overall, matching the primary order
merged = pd.merge(overall, sofifa_pivot, how='left', on='team_clean')
merged.drop(columns=['team_clean'], inplace=True)

# 6. Output: all original overallstats columns preserved, Sofifa stats joined as new columns
merged.to_csv('fifa_overall_with_sofifa_yearly.csv', index=False)

print('Merged file created: fifa_overall_with_sofifa_yearly.csv')
