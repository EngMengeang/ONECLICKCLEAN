import streamlit as st
import pandas as pd

from cleaner import drop_id_columns, remove_duplicates, handle_missing, remove_outliers, fix_categorical
from visualizer import draw_boxplots
from code_generator import generate_cleaning_script

st.set_page_config(page_title="OneClickClean", page_icon="🧹", layout="wide")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
    <h1 style='text-align:center; color:#4C9BE8;'>🧹 OneClickClean</h1>
    <p style='text-align:center; color:gray; font-size:16px;'>
        Upload your CSV and we'll automatically inspect, clean, and prepare it for you.
    </p>
    <hr>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/broom.png", width=80)
    st.title("OneClickClean")
    st.markdown("---")
    st.markdown("### 🗺️ Pipeline Steps")
    st.markdown("""
    1. 📂 Upload & Preview
    2. 🔍 Dataset Overview
    3. 🪪 Drop ID Columns
    4. 🗑️ Remove Duplicates
    5. 🩹 Handle Missing Values
    6. 📦 Detect & Remove Outliers
    7. 🔤 Fix Categorical Columns
    8. ⬇️ Download Cleaned CSV
    9. 🐍 Get Python Script
    """)
    st.markdown("---")
    st.caption("Built with Streamlit 🚀")

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown("## 📂 Step 1 — Upload Your CSV")
data = st.file_uploader("Drop your CSV file here", type="csv", label_visibility="collapsed")

if data:
    df = pd.read_csv(data)
    numerical = df.select_dtypes(include=["int64", "float64"]).columns.to_list()
    categorical = df.select_dtypes(include=["object", "string"]).columns.to_list()

    top_download = st.empty()

    # ── Step 2: Overview ─────────────────────────────────────────────────────
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
            "Dtype": df.dtypes.values,
        })
        st.dataframe(df_info, use_container_width=True)
    with st.expander("🔢 Numerical Columns"):
        st.dataframe(df[numerical].head(), use_container_width=True)
    with st.expander("🔤 Categorical Columns"):
        st.dataframe(df[categorical].head(), use_container_width=True)

    # ── Step 3: Drop ID Columns ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🪪 Step 3 — Drop ID Columns")
    df, id_cols = drop_id_columns(df)
    numerical = df.select_dtypes(include=["int64", "float64"]).columns.to_list()
    categorical = df.select_dtypes(include=["object", "string"]).columns.to_list()
    if id_cols:
        st.warning(f"🗑️ Dropped {len(id_cols)} ID column(s): {', '.join(id_cols)}")
    else:
        st.success("✅ No ID columns found.")

    # ── Step 4: Duplicates ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🗑️ Step 4 — Remove Duplicates")
    df, n_dup = remove_duplicates(df)
    d1, d2 = st.columns(2)
    d1.metric("Duplicates Found", n_dup)
    d2.metric("Duplicates Remaining", 0, delta=f"-{n_dup}", delta_color="inverse")
    st.success("✅ No duplicate rows found!" if n_dup == 0 else f"✅ Removed {n_dup} duplicate rows.")

    # ── Step 5: Missing Values ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🩹 Step 5 — Handle Missing Values")
    df, cols_under_5, cols_over_5_num, cols_over_5_cat, missing_summary = handle_missing(df, numerical, categorical)

    with st.expander("📊 Missing Value Summary", expanded=True):
        st.dataframe(missing_summary, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Dropped (< 5%)", len(cols_under_5), help="Rows dropped for these columns")
    m2.metric("Filled with Median", len(cols_over_5_num), help="Numerical cols >= 5% missing")
    m3.metric("Filled with Mode", len(cols_over_5_cat), help="Categorical cols >= 5% missing")
    if cols_over_5_num:
        st.info(f"📊 Filled with **median**: {', '.join(cols_over_5_num)}")
    if cols_over_5_cat:
        st.info(f"🔤 Filled with **mode**: {', '.join(cols_over_5_cat)}")
    st.success(f"✅ Missing values remaining: {df.isna().sum().sum()}")

    # ── Step 6: Outliers ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 📦 Step 6 — Detect & Remove Outliers")
    df_num_before = df.select_dtypes(include=["int64", "float64"])
    df, df_num, lower_bound, upper_bound, n_outliers = remove_outliers(df)

    st.warning(f"⚠️ Found **{n_outliers}** rows with outliers.")

    tab1, tab2 = st.tabs(["📊 Before Removing Outliers", "✅ After Removing Outliers"])
    with tab1:
        fig_before = draw_boxplots(df_num_before, "#4C9BE8", "Box Plots — Before")
        if fig_before:
            st.pyplot(fig_before)
    with tab2:
        df_num_clean = df.select_dtypes(include=["int64", "float64"])
        fig_after = draw_boxplots(df_num_clean, "#50C878", "Box Plots — After")
        if fig_after:
            st.pyplot(fig_after)

    o1, o2 = st.columns(2)
    o1.metric("Rows Before", len(df) + n_outliers)
    o2.metric("Rows After", len(df), delta=f"-{n_outliers}", delta_color="inverse")
    st.success(f"✅ Removed {n_outliers} outlier rows.")

    # ── Step 7: Categorical ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🔤 Step 7 — Fix Categorical Columns")
    cat_tab1, cat_tab2 = st.tabs(["Before Cleaning", "After Cleaning"])
    with cat_tab1:
        for c in categorical:
            if c in df.columns:
                st.write(f"**{c}:**", df[c].unique().tolist())
    df = fix_categorical(df, categorical)
    with cat_tab2:
        for c in categorical:
            if c in df.columns:
                st.write(f"**{c}:**", df[c].unique().tolist())
    st.success("✅ Categorical columns cleaned successfully!")

    # ── Step 8: Download CSV ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## ⬇️ Step 8 — Download Cleaned Data")
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
        use_container_width=True,
    )

    # ── Step 9: Python Script ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🐍 Step 9 — Get the Python Code")
    st.write("Copy or download the equivalent Python script to reproduce this cleaning pipeline.")

    python_code = generate_cleaning_script(cols_under_5, cols_over_5_num, cols_over_5_cat, categorical)
    st.code(python_code, language="python")
    st.download_button(
        label="⬇️ Download Python Script",
        data=python_code.encode("utf-8"),
        file_name="cleaning_script.py",
        mime="text/x-python",
        use_container_width=True,
    )

    # ── Quick Download (top placeholder) ─────────────────────────────────────
    with top_download.container():
        st.markdown("---")
        st.markdown("### ⚡ Quick Download")
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=cleaned_csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
            use_container_width=True,
            key="top_download_btn",
        )
        st.markdown("---")

else:
    st.markdown("""
        <div style='text-align:center; padding: 60px 0; color: gray;'>
            <h3>👆 Upload a CSV file to get started</h3>
            <p>Your data will be automatically cleaned in seconds.</p>
        </div>
    """, unsafe_allow_html=True)
