def generate_cleaning_script(
    cols_under_5: list,
    cols_over_5_num: list,
    cols_over_5_cat: list,
    categorical: list,
) -> str:
    """Generate a standalone Python cleaning script based on the detected columns."""

    return f'''import pandas as pd

df = pd.read_csv("your_file.csv")

# ── Remove duplicates ──────────────────────────────────
df = df.drop_duplicates()

# ── Handle missing values ──────────────────────────────
# Drop rows where missing < 5%
cols_under_5 = {repr(cols_under_5)}
df = df.dropna(subset=cols_under_5)

# Fill numerical columns (>= 5% missing) with median
cols_over_5_num = {repr(cols_over_5_num)}
for col in cols_over_5_num:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# Fill categorical columns (>= 5% missing) with mode
cols_over_5_cat = {repr(cols_over_5_cat)}
for col in cols_over_5_cat:
    if col in df.columns:
        mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
        df[col] = df[col].fillna(mode_val)

# ── Remove outliers (IQR method) ───────────────────────
df_num = df.select_dtypes(include=["int64", "float64"])
q1 = df_num.quantile(0.25)
q3 = df_num.quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
clean_mask = ((df_num >= lower_bound) & (df_num <= upper_bound)).all(axis=1)
df = df[clean_mask]

# ── Fix categorical inconsistencies ───────────────────
categorical = {repr(categorical)}
for col in categorical:
    if col in df.columns:
        df[col] = (
            df[col].astype(str).str.strip().str.lower()
            .str.replace(r"[^a-z0-9 _\\-]", "", regex=True)
            .str.replace(r"\\s+", " ", regex=True)
            .str.title()
        )

# ── Save cleaned data ──────────────────────────────────
df.to_csv("cleaned_data.csv", index=False)
print(f"Done! {{len(df)}} rows saved to cleaned_data.csv")
'''
