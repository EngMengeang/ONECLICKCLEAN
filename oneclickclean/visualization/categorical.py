import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


FEATURES = [
    {"key": "bar", "icon": "📈", "label": "Bar Chart"},
    {"key": "pie", "icon": "🥧", "label": "Pie Chart"},
    {"key": "count", "icon": "🔵", "label": "Count Plot"},
]


def _value_counts(df: pd.DataFrame, column: str, top_n: int) -> pd.DataFrame:
    """Return value counts for a column as a DataFrame with Value and Count."""
    counts = df[column].fillna("Missing").astype(str).value_counts().head(top_n).reset_index()
    counts.columns = ["Value", "Count"]
    return counts


def render_categorical(clean_data: pd.DataFrame):
    """Render categorical visualizations for cleaned dataset."""
    df = clean_data.copy()

    if df.empty or df.shape[1] == 0:
        st.info("No categorical columns to visualise.")
        return

    if "cat_chart" not in st.session_state:
        st.session_state.cat_chart = None

    st.markdown(
        "<p style='font-weight:600; font-size:15px; margin-bottom:6px;'>Choose a chart type:</p>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <style>
    .cat-card button {
        height: 80px !important;
        border-radius: 12px !important;
        border: 2px solid rgba(76,155,232,0.3) !important;
        background: linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%) !important;
        color: #e2e8f0 !important;
        font-size: 14px !important;
        transition: border-color .2s, transform .15s;
    }
    .cat-card button:hover { border-color:#4C9BE8 !important; transform:translateY(-2px); }
    .cat-card-active button {
        border-color:#4C9BE8 !important;
        box-shadow: 0 0 0 3px rgba(76,155,232,0.35);
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(FEATURES))
    for col, feat in zip(cols, FEATURES):
        with col:
            is_active = st.session_state.cat_chart == feat["key"]
            css = "cat-card" + (" cat-card-active" if is_active else "")
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(f"{feat['icon']}\n{feat['label']}", key=f"cat_{feat['key']}", use_container_width=True):
                st.session_state.cat_chart = feat["key"]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    chart = st.session_state.cat_chart
    if chart is None:
        st.info("☝️ Pick a chart type above to get started.")
        return

    col_name = st.selectbox("Select categorical column", df.columns.tolist(), key="cat_col")
    top_n = st.slider("Top categories to show", 3, 30, 10, key="cat_top_n")
    counts = _value_counts(df, col_name, top_n)

    if counts.empty:
        st.info("No values available for this column.")
        return

    if chart == "bar":
        st.subheader("📈 Bar Chart")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(counts["Value"], counts["Count"], color="#4C9BE8", alpha=0.9)
        ax.set_xlabel(col_name)
        ax.set_ylabel("Count")
        ax.set_title(f"Top {top_n} categories in {col_name}", fontweight="bold")
        ax.tick_params(axis="x", rotation=35)
        plt.tight_layout()
        st.pyplot(fig)
        st.dataframe(counts, use_container_width=True)

    elif chart == "pie":
        st.subheader("🥧 Pie Chart")
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(
            counts["Count"],
            labels=counts["Value"],
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 10},
        )
        ax.set_title(f"Top {top_n} categories in {col_name}", fontweight="bold")
        ax.axis("equal")
        st.pyplot(fig)
        st.dataframe(counts, use_container_width=True)

    elif chart == "count":
        st.subheader("🔵 Count Plot")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.countplot(
            data=df.fillna({col_name: "Missing"}),
            x=col_name,
            order=counts["Value"].tolist(),
            color="#4C9BE8",
            ax=ax,
        )
        ax.set_xlabel(col_name)
        ax.set_ylabel("Count")
        ax.set_title(f"Top {top_n} categories in {col_name}", fontweight="bold")
        ax.tick_params(axis="x", rotation=35)
        plt.tight_layout()
        st.pyplot(fig)
        st.dataframe(counts, use_container_width=True)
