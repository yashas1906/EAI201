import pandas as pd

num_tables = 17
tables = []

for i in range(1, num_tables + 1):
    filename = f"wiki_table_{i}_cleaned.csv"
    try:
        df = pd.read_csv(filename)
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
        tables.append(df)
        print(f"Loaded {filename}, shape: {df.shape}")
    except Exception as e:
        print(f"Error loading {filename}: {e}")

key_column = 'team'
tables_for_merge = [df for df in tables if key_column in df.columns]

if not tables_for_merge:
    print(f"No tables contain the key column '{key_column}'. Merge aborted.")
else:
    merged_df = tables_for_merge[0]
    for df in tables_for_merge[1:]:
        merged_df = pd.merge(merged_df, df, on=key_column, how='outer', suffixes=('', '_dup'))
        cols_to_drop = [col for col in merged_df.columns if col.endswith('_dup')]
        merged_df.drop(columns=cols_to_drop, inplace=True)

    merged_df.to_csv("wiki_merged_team_tables.csv", index=False)
    print("Merged Wikipedia team-related tables saved as wiki_merged_team_tables.csv")
