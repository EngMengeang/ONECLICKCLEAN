import streamlit as st
import pandas as pd
from Data_Visualization.Categorical import render_categorical
from Data_Visualization.Numerical import render_numerical


def render_visualization():
    """Main visualization page — shows cleaned data info and chart tabs."""
    st.markdown("## 📊 Data Visualization")

    if "df_clean" not in st.session_state or st.session_state.df_clean is None:
        st.warning("⚠️ No cleaned data found. Please run **Data Cleaning** first, then come back here.")
        return

    df_clean = st.session_state.df_clean
    numerical_raw = df_clean.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_raw = df_clean.select_dtypes(include=["object", "string"]).columns.tolist()
    st.success(f"✅ Loaded cleaned data — **{df_clean.shape[0]}** rows × **{df_clean.shape[1]}** columns")

    # Chart tabs — add more tabs here as you build new charts
    tab_bar, = st.tabs(["📊 Numerical Variable"])
    with tab_bar:
        render_numerical(df_clean[numerical_raw])

    tab_bar, = st.tabs(["📊 Categorical Variable"])
    with tab_bar:
        render_categorical(df_clean[categorical_raw])
