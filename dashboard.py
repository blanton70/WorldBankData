# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Merged Country Indicator Dashboard")

# Load and merge data files
@st.cache_data
def load_and_merge():
    # Load df1
    df1 = pd.read_csv("df1.csv", header=None)
    df1.columns = ["country", "indicator", "year", "value", "year_short"]
    
    # Load df2
    df2 = pd.read_csv("df2.csv", header=None)
    df2.columns = ["country", "indicator", "year", "value", "year_short"]
    
    # Drop unnecessary column
    df1 = df1.drop(columns=["year_short"])
    df2 = df2.drop(columns=["year_short"])
    
    # Combine both datasets
    df = pd.concat([df1, df2], ignore_index=True)
    
    # Clean and convert
    df['year'] = df['year'].astype(int)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    return df

data = load_and_merge()

# -- UI CONTROLS --

# Year slider
year = st.slider("Select year", int(data['year'].min()), int(data['year'].max()), step=1)

# Filter data by year
year_data = data[data['year'] == year]

# Country selection
countries = sorted(year_data['country'].dropna().unique())
selected_countries = st.multiselect("Select countries", countries, default=countries[:5])

filtered = year_data[year_data['country'].isin(selected_countries)]

# Pivot: each row = country, each column = indicator
pivot = filtered.pivot(index="country", columns="indicator", values="value").reset_index()

# Indicators for axes
available_indicators = sorted(filtered['indicator'].dropna().unique())
x_indicator = st.selectbox("X-axis indicator", available_indicators, index=0)
y_indicator = st.selectbox("Y-axis indicator", available_indicators, index=1)

# Log/linear scale
scale = st.radio("Y-axis scale", ["Linear", "Logarithmic"], horizontal=True)
log_y = scale == "Logarithmic"

# Plot scatter
if x_indicator in pivot.columns and y_indicator in pivot.columns:
    fig = px.scatter(
        pivot,
        x=x_indicator,
        y=y_indicator,
        text="country",
        log_y=log_y,
        title=f"{y_indicator} vs {x_indicator} ({year}, {scale})"
    )
    fig.update_traces(marker=dict(size=12), textposition='top center')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Selected indicators are not available for the selected countries and year.")
