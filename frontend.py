import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.title("OneClickClean 🚀")
st.write("Upload your CSV and it will automatically clean it!")

# Upload CSV
data = st.file_uploader("Choose a CSV file", type="csv")

if data:

    # read the csv file
    st.subheader("Read the CSV File")
    df = pd.read_csv(data)
    
    # Observe the data
    st.subheader("Observe the data")
    st.dataframe(df.head())

    # part 1 Inspect the dataset size
    st.subheader("1. Inspect dataset size, structure  and data types")
    st.write("Dataset Size")

    # check the dataset shape
    row, col = df.shape
    st.write(f"There are {row} row and {col} col")

    # show the dataset info  
    st.subheader("Dataset Infomation ")
    df_info = pd.DataFrame({
    "Column": df.columns,
    "Non-Null Count": df.notnull().sum().values,
    "Dtype": df.dtypes.values
    })

    st.dataframe(df_info)

    # data type
    st.subheader("Check the datattype")
    numerical = df.select_dtypes(include=['int64', 'float64']).columns.to_list()
    categorical = df.select_dtypes(include=['string', 'object']).columns.to_list()
    st.write("Numerical column")
    st.write(numerical)

    st.write("Categorical column")
    st.write(categorical)

    # data  structure 
    st.subheader("Data Structure")
    st.write("Numerical ")
    st.dataframe(df[numerical].head())\
    
    st.write("Categorical")
    st.dataframe(df[categorical].head())