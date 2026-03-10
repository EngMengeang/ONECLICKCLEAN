import streamlit as st
import pandas as pd

from cleaner import drop_id_columns, remove_duplicates, handle_missing, remove_outliers, fix_categorical
from visualizer import draw_boxplots
from code_generator import generate_cleaning_script
from Data_Visualization.Visual import render_visualization

st.set_page_config(page_title="OneClickClean", page_icon="🧹", layout="wide")

# ── Session state ─────────────────────────────────────────────────────────────
if "feature" not in st.session_state:
    st.session_state.feature = None

# ── Global style ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color: #e2e8f0 !important; }

/* Feature card buttons — uniform height & layout */
.feature-card button {
    height: 160px !important;
    border-radius: 16px !important;
    border: 2px solid rgba(76,155,232,0.3) !important;
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%) !important;
    color: #e2e8f0 !important;
    transition: border-color .25s, transform .2s, box-shadow .25s;
    padding: 16px 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    white-space: pre-line !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
}
.feature-card button:hover {
    border-color: #4C9BE8 !important;
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(76,155,232,0.18);
}
.feature-card-active button {
    border-color: #4C9BE8 !important;
    background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%) !important;
    box-shadow: 0 0 0 3px rgba(76,155,232,0.35), 0 8px 24px rgba(76,155,232,0.12);
}
.feature-card-disabled button {
    opacity: 0.45 !important;
    cursor: not-allowed !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/broom.png", width=80)
    st.title("OneClickClean")
    st.markdown("---")
    if st.session_state.feature == "cleaning":
        st.markdown("### 🗺️ Pipeline Steps")
        st.markdown("""
1. 🔍 Dataset Overview
2. 🪪 Drop ID Columns
3. 🗑️ Remove Duplicates
4. 🩹 Handle Missing Values
5. 📦 Detect & Remove Outliers
6. 🔤 Fix Categorical Columns
7. ⬇️ Download Cleaned CSV
8. 🐍 Get Python Script
        """)
    elif st.session_state.feature == "visualization":
        st.markdown("### 📊 Visualization")
        st.markdown("""
- Box Plots (before / after outlier removal)
- More charts coming soon!
        """)
    else:
        st.markdown("### 👋 Welcome!")
        st.markdown("Upload a CSV file then choose a feature to get started.")
    st.markdown("---")
    st.caption("Built with Streamlit 🚀")

# ─────────────────────────────────────────────────────────────────────────────
# LANDING — Header + Upload
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
    <h1 style='text-align:center; color:#4C9BE8;'>🧹 OneClickClean</h1>
    <p style='text-align:center; color:gray; font-size:17px;'>
        Upload your CSV file and explore powerful features below.
    </p>
    <hr>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CSV UPLOAD — always on top
# ─────────────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("📂 Drop your CSV file here to get started", type="csv")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE CARDS — always visible
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='text-align:center; color:#e2e8f0;'>✨ Choose a Feature</h3>",
    unsafe_allow_html=True,
)

FEATURES = [
    {
        "key": "cleaning",
        "icon": "🧹",
        "title": "Data Cleaning",
        "desc": "Auto-clean your dataset:\nduplicates, missing values,\noutliers & more",
        "disabled": False,
    },
    {
        "key": "visualization",
        "icon": "📊",
        "title": "Visualization",
        "desc": "Explore your data with\ninteractive charts\n& visual insights",
        "disabled": False,
    },
    {
        "key": "coming_soon",
        "icon": "🔮",
        "title": "Coming Soon",
        "desc": "More powerful features\nare on the way —\nstay tuned!",
        "disabled": True,
    },
]

cards = st.columns(len(FEATURES))
for col, feat in zip(cards, FEATURES):
    with col:
        is_active = st.session_state.feature == feat["key"]
        css_cls = "feature-card"
        if is_active:
            css_cls += " feature-card-active"
        if feat["disabled"]:
            css_cls += " feature-card-disabled"

        label = f"{feat['icon']}  {feat['title']}\n\n{feat['desc']}"
        st.markdown(f'<div class="{css_cls}">', unsafe_allow_html=True)
        if st.button(label, use_container_width=True, key=f"btn_{feat['key']}", disabled=feat["disabled"]):
            st.session_state.feature = feat["key"]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# NO FEATURE SELECTED — prompt user
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.feature is None:
    if uploaded:
        df_raw = pd.read_csv(uploaded)
        r, c = df_raw.shape
        numerical_raw = df_raw.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categorical_raw = df_raw.select_dtypes(include=["object", "string"]).columns.tolist()
        st.markdown("#### 👀 File Preview")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📏 Rows", r)
        m2.metric("📐 Columns", c)
        m3.metric("🔢 Numerical", len(numerical_raw))
        m4.metric("🔤 Categorical", len(categorical_raw))
        st.dataframe(df_raw.head(), use_container_width=True)
    st.info("☝️ Pick a feature above to continue.")

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE: DATA CLEANING
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.feature == "cleaning":
    if not uploaded:
        st.warning("📂 Please upload a CSV file above to start the cleaning pipeline.")
    else:
        df_raw = pd.read_csv(uploaded)
        df = df_raw.copy()
        numerical = df.select_dtypes(include=["int64", "float64"]).columns.to_list()
        categorical = df.select_dtypes(include=["object", "string"]).columns.to_list()

        st.markdown("## 🧹 Data Cleaning Pipeline")

        # Step 1: Overview ─────────────────────────────────────────────────────
        st.markdown("## 🔍 Step 1 — Dataset Overview")
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

        # Step 2: Drop ID Columns ──────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 🪪 Step 2 — Drop ID Columns")
        df, id_cols = drop_id_columns(df)
        numerical = df.select_dtypes(include=["int64", "float64"]).columns.to_list()
        categorical = df.select_dtypes(include=["object", "string"]).columns.to_list()
        if id_cols:
            st.warning(f"🗑️ Dropped {len(id_cols)} ID column(s): {', '.join(id_cols)}")
        else:
            st.success("✅ No ID columns found.")

        # Step 3: Duplicates ───────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 🗑️ Step 3 — Remove Duplicates")
        df, n_dup = remove_duplicates(df)
        d1, d2 = st.columns(2)
        d1.metric("Duplicates Found", n_dup)
        d2.metric("Duplicates Remaining", 0, delta=f"-{n_dup}", delta_color="inverse")
        st.success("✅ No duplicate rows found!" if n_dup == 0 else f"✅ Removed {n_dup} duplicate rows.")

        # Step 4: Missing Values ───────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 🩹 Step 4 — Handle Missing Values")
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

        # Step 5: Outliers ─────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 📦 Step 5 — Detect & Remove Outliers")
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

        # Step 6: Categorical ──────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 🔤 Step 6 — Fix Categorical Columns")

        if not categorical:
            st.info("ℹ️ No categorical columns found.")
        else:
            st.write(f"Found **{len(categorical)}** categorical column(s): {', '.join([c for c in categorical if c in df.columns])}")

            with st.expander("👁️ Before Cleaning — click to view unique values"):
                for c in categorical:
                    if c in df.columns:
                        vc = df[c].value_counts().reset_index()
                        vc.columns = ["Value", "Count"]
                        st.markdown(f"**{c}** — {df[c].nunique()} unique values")
                        st.dataframe(vc, use_container_width=True, height=200)

            df = fix_categorical(df, categorical)

            with st.expander("✅ After Cleaning — click to view unique values"):
                for c in categorical:
                    if c in df.columns:
                        vc = df[c].value_counts().reset_index()
                        vc.columns = ["Value", "Count"]
                        st.markdown(f"**{c}** — {df[c].nunique()} unique values")
                        st.dataframe(vc, use_container_width=True, height=200)

        st.success("✅ Categorical columns cleaned successfully!")

        # Step 7: Download CSV ─────────────────────────────────────────────────
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
            file_name=f"{uploaded.name.removesuffix('.csv')}_cleaned_data.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Step 8: Python Script ────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 🐍 Step 8 — Get the Python Code")
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

        # Save cleaned dataframe to session state for other features
        st.session_state.df_clean = df.copy()

    # ─────────────────────────────────────────────────────────────────────────
    # FEATURE: VISUALIZATION
    # ─────────────────────────────────────────────────────────────────────────
elif st.session_state.feature == "visualization":
    render_visualization()

