import pandas as pd


def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove duplicate rows. Returns cleaned df and count removed."""
    before = len(df)
    df = df.drop_duplicates()
    return df, before - len(df)


def handle_missing(df: pd.DataFrame, numerical: list, categorical: list):
    """
    Handle missing values:
    - < 5%  → drop rows
    - >= 5% numerical  → fill with median
    - >= 5% categorical → fill with mode

    Returns (df, cols_under_5, cols_over_5_num, cols_over_5_cat, missing_summary_df)
    """
    missing = df.isna().sum().reset_index()
    missing.columns = ["Column", "Missing Count"]
    missing["Missing (%)"] = (missing["Missing Count"] / len(df) * 100).round(2).astype(str) + "%"
    missing["Has Missing"] = missing["Missing Count"].apply(lambda x: "⚠️ Yes" if x > 0 else "✅ No")
    summary_df = missing.copy()

    missing["Missing (%)"] = missing["Missing (%)"].str.replace("%", "").astype("float64")

    # only columns that actually have some missing but < 5% → drop rows
    cols_under_5 = missing[
        (missing["Missing (%)"] > 0) & (missing["Missing (%)"] < 5)
    ]["Column"].tolist()
    cols_over_5_num = missing[
        (missing["Missing (%)"] >= 5) & (missing["Column"].isin(numerical))
    ]["Column"].tolist()
    cols_over_5_cat = missing[
        (missing["Missing (%)"] >= 5) & (missing["Column"].isin(categorical))
    ]["Column"].tolist()

    # drop rows for columns with 0% < missing < 5%
    if cols_under_5:
        df = df.dropna(subset=cols_under_5)

    # fill numerical >= 5% with median
    for col in cols_over_5_num:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # fill categorical >= 5% with mode
    for col in cols_over_5_cat:
        if col in df.columns:
            mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(mode_val)

    return df, cols_under_5, cols_over_5_num, cols_over_5_cat, summary_df


def remove_outliers(df: pd.DataFrame):
    """
    Remove outliers using the IQR method on numerical columns.
    Returns (cleaned_df, df_num_before, lower_bound, upper_bound, n_removed)
    """
    df_num = df.select_dtypes(include=["int64", "float64"])
    q1 = df_num.quantile(0.25)
    q3 = df_num.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    before = len(df)
    clean_mask = ((df_num >= lower_bound) & (df_num <= upper_bound)).all(axis=1)
    df = df[clean_mask]

    return df, df_num, lower_bound, upper_bound, before - len(df)


def fix_categorical(df: pd.DataFrame, categorical: list) -> pd.DataFrame:
    """Normalise categorical columns: strip, lowercase, remove special chars, title case."""
    for col in categorical:
        if col in df.columns:
            df[col] = (
                df[col].astype(str).str.strip().str.lower()
                .str.replace(r"[^a-z0-9 _\-]", "", regex=True)
                .str.replace(r"\s+", " ", regex=True)
                .str.title()
            )
    return df
