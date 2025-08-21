import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Country Dashboard", layout="wide")
st.title("📊 Merged Country Indicator Dashboard")

# --- Data loading and merging ---
@st.cache_data
def load_and_merge():
    # Load the first CSV file
    df1 = pd.read_csv("df1.csv", header=None)
    df1.columns = ["country", "indicator", "year", "value", "year_short"]

    # Load the second CSV file
    df2 = pd.read_csv("df2.csv", header=None)
    df2.columns = ["country", "indicator", "year", "value", "year_short"]

    # Drop unnecessary column
    df1 = df1.drop(columns=["year_short"])
    df2 = df2.drop(columns=["year_short"])

    # Combine datasets
    df = pd.concat([df1, df2], ignore_index=True)

    # Safely convert data types
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    return df

# Load data
data = load_and_merge()

# --- User Inputs ---

# Select year with slider
min_year = int(data['year'].min())
max_year = int(data['year'].max())
selected_year = st.slider("Select Year", min_year, max_year, value=max_year)

# Filter data for the selected year
year_data = data[data['year'] == selected_year]

# Get list of countries
all_countries = sorted(year_data['country'].dropna().unique())

# --- Layout with columns ---

col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.subheader("Country Selection")
    select_all = st.checkbox("Select all countries", value=False)
    if select_all:
        selected_countries = st.multiselect(
            "Select Countries",
            options=all_countries,
            default=all_countries,
            key="countries"
        )
    else:
        selected_countries = st.multiselect(
            "Select Countries",
            options=all_countries,
            default=all_countries[:5],
            key="countries"
        )

with col2:
    available_indicators = sorted(year_data['indicator'].dropna().unique())
    x_indicator = st.selectbox("X-axis Indicator", available_indicators, index=0, key="x_ind")

with col3:
    y_indicator = st.selectbox("Y-axis Indicator", available_indicators, index=1, key="y_ind")

# Radio buttons for scale under columns (full width)
st.markdown("---")
y_scale = st.radio("Y-axis Scale", ["Linear", "Logarithmic"], horizontal=True, key="scale")
log_y = y_scale == "Logarithmic"

# --- Filtering and Plotting ---

filtered = year_data[year_data['country'].isin(selected_countries)]

# Pivot to get one row per country, columns as indicators
pivot = filtered.pivot(index="country", columns="indicator", values="value").reset_index()

# Plot if indicators available
if x_indicator in pivot.columns and y_indicator in pivot.columns:
    fig = px.scatter(
        pivot,
        x=x_indicator,
        y=y_indicator,
        text="country",
        log_y=log_y,
        title=f"{y_indicator} vs {x_indicator} in {selected_year} ({y_scale} scale)",
        height=600
    )
    fig.update_traces(marker=dict(size=12), textposition="top center")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("One or both selected indicators are not available for the chosen countries and year.")
