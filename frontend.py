import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="OneClickClean", page_icon="🧹", layout="wide")

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
    <h1 style='text-align:center; color:#4C9BE8;'>🧹 OneClickClean</h1>
    <p style='text-align:center; color:gray; font-size:16px;'>
        Upload your CSV and we'll automatically inspect, clean, and prepare it for you.
    </p>
    <hr>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/broom.png", width=80)
    st.title("OneClickClean")
    st.markdown("---")
    st.markdown("### 🗺️ Pipeline Steps")
    st.markdown("""
    1. 📂 Upload & Preview  
    2. 🔍 Dataset Overview  
    3. 🗑️ Remove Duplicates  
    4. 🩹 Handle Missing Values  
    5. 📦 Detect & Remove Outliers  
    6. 🔤 Fix Categorical Columns  
    7. ⬇️ Download Cleaned CSV  
    """)
    st.markdown("---")
    st.caption("Built with Streamlit 🚀")

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown("## 📂 Step 1 — Upload Your CSV")
data = st.file_uploader("Drop your CSV file here", type="csv", label_visibility="collapsed")

if data:
    df = pd.read_csv(data)
    numerical = df.select_dtypes(include=['int64', 'float64']).columns.to_list()
    categorical = df.select_dtypes(include=['object', 'string']).columns.to_list()

    # ── Quick Download Bar (top) ──────────────────────────────────────────────
    top_download = st.empty()

    # ── Preview ───────────────────────────────────────────────────────────────
    st.markdown("## 🔍 Step 2 — Dataset Overview")

    row, col = df.shape
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📏 Rows", row)
    c2.metric("📐 Columns", col)
    c3.metric("🔢 Numerical", len(numerical))
    c4.metric("🔤 Categorical", len(categorical))

    with st.expander("👀 Preview Data (first 5 rows)", expanded=True):
        st.dataframe(df.head(), use_container_width=True)

    with st.expander("📋 Column Info"):
        df_info = pd.DataFrame({
            "Column": df.columns,
            "Non-Null Count": df.notnull().sum().values,
            "Dtype": df.dtypes.values
        })
        st.dataframe(df_info, use_container_width=True)

    with st.expander("🔢 Numerical Columns"):
        st.dataframe(df[numerical].head(), use_container_width=True)

    with st.expander("🔤 Categorical Columns"):
        st.dataframe(df[categorical].head(), use_container_width=True)

    # ── Duplicates ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🗑️ Step 3 — Remove Duplicates")
    dup_before = df.duplicated().sum()
    df = df.drop_duplicates()
    dup_after = df.duplicated().sum()
    d1, d2 = st.columns(2)
    d1.metric("Duplicates Found", dup_before, delta=None)
    d2.metric("Duplicates After Removal", dup_after, delta=f"-{dup_before - dup_after}", delta_color="inverse")
    if dup_before == 0:
        st.success("✅ No duplicate rows found!")
    else:
        st.success(f"✅ Removed {dup_before} duplicate rows.")

    # ── Missing Values ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🩹 Step 4 — Handle Missing Values")

    missing = df.isna().sum().reset_index()
    missing.columns = ["Column", "Missing Count"]
    missing["Missing (%)"] = (missing["Missing Count"] / len(df) * 100).round(2).astype(str) + "%"
    missing["Has Missing"] = missing["Missing Count"].apply(lambda x: "⚠️ Yes" if x > 0 else "✅ No")

    with st.expander("📊 Missing Value Summary", expanded=True):
        st.dataframe(missing, use_container_width=True)

    missing["Missing (%)"] = missing["Missing (%)"].str.replace("%", "").astype("float64")

    cols_under_5 = missing[missing["Missing (%)"] < 5]["Column"].tolist()
    cols_over_5_num = missing[
        (missing["Missing (%)"] >= 5) & (missing["Column"].isin(numerical))
    ]["Column"].tolist()
    cols_over_5_cat = missing[
        (missing["Missing (%)"] >= 5) & (missing["Column"].isin(categorical))
    ]["Column"].tolist()

    # drop rows where missing < 5%
    df[cols_under_5] = df[cols_under_5]
    df = df.dropna(subset=cols_under_5)

    # fill numerical >= 5% with median
    for col in cols_over_5_num:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # fill categorical >= 5% with mode
    for col in cols_over_5_cat:
        if col in df.columns:
            mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(mode_val)

    # summary
    m1, m2, m3 = st.columns(3)
    m1.metric("Dropped (< 5% missing)", len(cols_under_5), help="Rows with nulls dropped for these columns")
    m2.metric("Filled with Median", len(cols_over_5_num), help="Numerical columns ≥ 5% missing")
    m3.metric("Filled with Mode", len(cols_over_5_cat), help="Categorical columns ≥ 5% missing")

    if cols_over_5_num:
        st.info(f"📊 Filled with **median**: {', '.join(cols_over_5_num)}")
    if cols_over_5_cat:
        st.info(f"🔤 Filled with **mode**: {', '.join(cols_over_5_cat)}")
    st.success(f"✅ Missing values remaining: {df.isna().sum().sum()}")

    # ── Outliers ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 📦 Step 5 — Detect & Remove Outliers")

    df_num = df.select_dtypes(include=['int64', 'float64'])
    q1 = df_num.quantile(0.25)
    q3 = df_num.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_mask = (df_num < lower_bound) | (df_num > upper_bound)
    outlier = df_num[outlier_mask.any(axis=1)]
    st.warning(f"⚠️ Found **{len(outlier)}** rows with outliers.")

    def draw_boxplots(data, color, title):
        cols_list = data.columns.tolist()
        if not cols_list:
            return
        n_c, n_r = 2, -(-len(cols_list) // 2)
        fig, axes = plt.subplots(n_r, n_c, figsize=(14, n_r * 4))
        fig.suptitle(title, fontsize=14, fontweight="bold", y=1.01)
        axes = axes.flatten() if n_r * n_c > 1 else [axes]
        for i, c in enumerate(cols_list):
            axes[i].boxplot(data[c].dropna(), patch_artist=True,
                            boxprops=dict(facecolor=color, color="#1a1a2e"),
                            medianprops=dict(color="red", linewidth=2),
                            flierprops=dict(marker="o", color="orange", markersize=5))
            axes[i].set_title(c, fontsize=11, fontweight="bold")
            axes[i].set_ylabel("Value")
        for j in range(len(cols_list), len(axes)):
            axes[j].set_visible(False)
        plt.tight_layout()
        return fig

    tab1, tab2 = st.tabs(["📊 Before Removing Outliers", "✅ After Removing Outliers"])

    with tab1:
        fig_before = draw_boxplots(df_num, "#4C9BE8", "Box Plots — Before")
        if fig_before:
            st.pyplot(fig_before)

    before = len(df)
    clean_mask = ((df_num >= lower_bound) & (df_num <= upper_bound)).all(axis=1)
    df = df[clean_mask]
    after = len(df)

    with tab2:
        df_num_clean = df.select_dtypes(include=['int64', 'float64'])
        fig_after = draw_boxplots(df_num_clean, "#50C878", "Box Plots — After")
        if fig_after:
            st.pyplot(fig_after)

    o1, o2 = st.columns(2)
    o1.metric("Rows Before", before)
    o2.metric("Rows After Outlier Removal", after, delta=f"-{before - after}", delta_color="inverse")
    st.success(f"✅ Removed {before - after} outlier rows.")

    # ── Categorical Cleaning ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🔤 Step 6 — Fix Categorical Columns")

    cat_tab1, cat_tab2 = st.tabs(["Before Cleaning", "After Cleaning"])

    with cat_tab1:
        for c in categorical:
            if c in df.columns:
                st.write(f"**{c}:**", df[c].unique().tolist())

    for c in categorical:
        if c in df.columns:
            df[c] = (
                df[c].astype(str).str.strip().str.lower()
                .str.replace(r"[^a-z0-9 _\-]", "", regex=True)
                .str.replace(r"\s+", " ", regex=True)
                .str.title()
            )

    with cat_tab2:
        for c in categorical:
            if c in df.columns:
                st.write(f"**{c}:**", df[c].unique().tolist())

    st.success("✅ Categorical columns cleaned successfully!")

    # ── Download ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## ⬇️ Step 7 — Download Cleaned Data")

    final_rows, final_cols = df.shape
    f1, f2, f3 = st.columns(3)
    f1.metric("Final Rows", final_rows)
    f2.metric("Final Columns", final_cols)
    f3.metric("Rows Removed", row - final_rows)

    with st.expander("👀 Preview Cleaned Data"):
        st.dataframe(df.head(10), use_container_width=True)

    cleaned_csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Cleaned CSV",
        data=cleaned_csv,
        file_name="cleaned_data.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ── Generated Python Code ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🐍 Step 8 — Get the Python Code")
    st.write("Copy or download the equivalent Python script to reproduce this cleaning pipeline.")

    cols_under_5_repr = repr(cols_under_5)
    cols_over_5_num_repr = repr(cols_over_5_num)
    cols_over_5_cat_repr = repr(cols_over_5_cat)
    categorical_repr = repr(categorical)

    python_code = f'''import pandas as pd

df = pd.read_csv("your_file.csv")

# ── Remove duplicates ──────────────────────────────────
df = df.drop_duplicates()

# ── Handle missing values ──────────────────────────────
# Drop rows where missing < 5%
cols_under_5 = {cols_under_5_repr}
df = df.dropna(subset=cols_under_5)

# Fill numerical columns (>= 5% missing) with median
cols_over_5_num = {cols_over_5_num_repr}
for col in cols_over_5_num:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# Fill categorical columns (>= 5% missing) with mode
cols_over_5_cat = {cols_over_5_cat_repr}
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
categorical = {categorical_repr}
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

    st.code(python_code, language="python")

    st.download_button(
        label="⬇️ Download Python Script",
        data=python_code.encode("utf-8"),
        file_name="cleaning_script.py",
        mime="text/x-python",
        use_container_width=True
    )

    # fill the top placeholder now that the cleaned CSV is ready
    with top_download.container():
        st.markdown("---")
        st.markdown("### ⚡ Quick Download")
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=cleaned_csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
            use_container_width=True,
            key="top_download_btn"
        )
        st.markdown("---")

else:
    st.markdown("""
        <div style='text-align:center; padding: 60px 0; color: gray;'>
            <h3>👆 Upload a CSV file to get started</h3>
            <p>Your data will be automatically cleaned in seconds.</p>
        </div>
    """, unsafe_allow_html=True)