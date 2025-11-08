import pandas as pd

# Load your dataset (adjust path if needed)
df = pd.read_csv('fifa_overall_with_all_sofifa_years.csv')

# Separate numeric and categorical columns
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
categorical_cols = df.select_dtypes(include=['object']).columns

# Step 1: Impute numeric columns with median
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

# Step 2: Impute categorical columns with mode or 'Unknown'
for col in categorical_cols:
    mode_val = df[col].mode()
    if not mode_val.empty:
        df[col].fillna(mode_val[0], inplace=True)
    else:
        df[col].fillna('Unknown', inplace=True)

# Step 3: (Optional) Add missing indicators for columns where NaNs existed
for col in df.columns:
    if df[col].isnull().any():
        df[f'{col}_missing'] = df[col].isnull().astype(int)

# Now df has missing values imputed, you can proceed to modeling directly
print("Missing data handled")
