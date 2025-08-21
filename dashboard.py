# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🌍 Country Data Dashboard")

# Load data
df1 = pd.read_csv("data1.csv")
df2 = pd.read_csv("data2.csv")

# Merge datasets on 'country' or 'Country'
df = pd.merge(df1, df2, on="country", how="outer")

# Dropdown to choose country
country_list = sorted(df['country'].dropna().unique())
selected_country = st.selectbox("Select a country", country_list)

# Show data for the selected country
country_data = df[df['country'] == selected_country]
st.write("### Data for", selected_country)
st.dataframe(country_data)

# Optional: plot a numerical column
numeric_cols = country_data.select_dtypes(include='number').columns.tolist()
if numeric_cols:
    selected_col = st.selectbox("Select column to plot", numeric_cols)
    fig = px.bar(country_data, x="country", y=selected_col, title=f"{selected_col} for {selected_country}")
    st.plotly_chart(fig)
else:
    st.write("No numeric data available to plot.")
