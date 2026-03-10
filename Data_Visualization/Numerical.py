import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

FEATURES = [
    {"key": "histogram", "icon": "📈", "label": "Histogram"},
    {"key": "box",       "icon": "🔲", "label": "Box Plot"},
    {"key": "scatter",   "icon": "🔵", "label": "Scatter "},
    {"key": "line",      "icon": "📉", "label": "Line Chart"},
    {"key": "cor",      "icon": "�", "label": "Correlation"}
]


def render_numerical(clean_data: pd.DataFrame):
    df = clean_data

    if df.empty or df.shape[1] == 0:
        st.info("No numerical columns to visualise.")
        return

    # ── Chart selector cards ──────────────────────────────────────────────────
    if "num_chart" not in st.session_state:
        st.session_state.num_chart = None

    st.markdown(
        "<p style='font-weight:600; font-size:15px; margin-bottom:6px;'>Choose a chart type:</p>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <style>
    .num-card button {
        height: 80px !important;
        border-radius: 12px !important;
        border: 2px solid rgba(76,155,232,0.3) !important;
        background: linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%) !important;
        color: #e2e8f0 !important;
        font-size: 14px !important;
        transition: border-color .2s, transform .15s;
    }
    .num-card button:hover { border-color:#4C9BE8 !important; transform:translateY(-2px); }
    .num-card-active button {
        border-color:#4C9BE8 !important;
        box-shadow: 0 0 0 3px rgba(76,155,232,0.35);
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(FEATURES))
    for col, feat in zip(cols, FEATURES):
        with col:
            is_active = st.session_state.num_chart == feat["key"]
            css = "num-card" + (" num-card-active" if is_active else "")
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(f"{feat['icon']}\n{feat['label']}", key=f"num_{feat['key']}", use_container_width=True):
                st.session_state.num_chart = feat["key"]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Chart content ─────────────────────────────────────────────────────────
    chart = st.session_state.num_chart

    if chart is None:
        st.info("☝️ Pick a chart type above to get started.")

    elif chart == "histogram":
        st.subheader("📈 Histogram")
        col = st.selectbox("Select column", df.columns.tolist(), key="hist_col")
        bins = st.slider("Bins", 5, 100, 30, key="hist_bins")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(df[col].dropna(), bins=bins, color="#4C9BE8", edgecolor="white", alpha=0.85)
        ax.set_xlabel(col); ax.set_ylabel("Frequency")
        ax.set_title(f"Distribution of {col}", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    elif chart == "box":
        st.subheader("🔲 Box Plot")
        selected = st.multiselect("Select columns", df.columns.tolist(), default=df.columns.tolist()[:4], key="box_cols")
        if selected:
            fig, ax = plt.subplots(figsize=(max(8, len(selected) * 2), 5))
            df[selected].boxplot(ax=ax, patch_artist=True)
            ax.set_title("Box Plots", fontweight="bold")
            plt.tight_layout()
            st.pyplot(fig)

    elif chart == "scatter":
        st.subheader("🔵 Scatter Plot")
        c1, c2 = st.columns(2)
        x = c1.selectbox("X axis", df.columns.tolist(), key="sc_x")
        y = c2.selectbox("Y axis", df.columns.tolist(), index=min(1, len(df.columns) - 1), key="sc_y")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(df[x], df[y], color="#4C9BE8", alpha=0.65, s=40)
        ax.set_xlabel(x); ax.set_ylabel(y)
        ax.set_title(f"{x}  vs  {y}", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    elif chart == "line":
        st.subheader("📉 Line Chart")
        selected = st.multiselect("Select columns", df.columns.tolist(), default=df.columns.tolist()[:2], key="line_cols")
        if selected:
            fig, ax = plt.subplots(figsize=(12, 4))
            for c in selected:
                ax.plot(df[c].values, label=c, linewidth=1.5)
            ax.set_xlabel("Index"); ax.set_ylabel("Value")
            ax.set_title("Line Chart", fontweight="bold")
            ax.legend()
            plt.tight_layout()
            st.pyplot(fig)
    elif chart == "cor":
        st.subheader("🔥 LM Plot (Regression)")
        c1, c2 = st.columns(2)
        x = c1.selectbox("X axis", df.columns.tolist(), key="cor_x")
        y = c2.selectbox("Y axis", df.columns.tolist(), index=min(1, len(df.columns) - 1), key="cor_y")
        plot = sns.lmplot(data=df, x=x, y=y, height=5, aspect=1.8, ci=None,
                          scatter_kws={"color": "#4C9BE8", "alpha": 0.65, "s": 40},
                          line_kws={"color": "#e05c5c"})
        plot.set_axis_labels(x, y)
        st.pyplot(plot.figure)