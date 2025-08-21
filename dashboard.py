import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Country Dashboard", layout="wide")
st.title("📊 Merged Country Indicator Dashboard")

@st.cache_data
def load_and_merge():
    df1 = pd.read_csv("df1.csv", header=None)
    df1.columns = ["country", "indicator", "year", "value", "year_short"]
    df2 = pd.read_csv("df2.csv", header=None)
    df2.columns = ["country", "indicator", "year", "value", "year_short"]
    df1 = df1.drop(columns=["year_short"])
    df2 = df2.drop(columns=["year_short"])
    df = pd.concat([df1, df2], ignore_index=True)
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df

data = load_and_merge()

min_year = int(data['year'].min())
max_year = int(data['year'].max())
selected_year = st.slider("Select Year", min_year, max_year, value=max_year)

year_data = data[data['year'] == selected_year]

all_countries = sorted(year_data['country'].dropna().unique())
available_indicators = sorted(year_data['indicator'].dropna().unique())

# Layout for controls and plot
col_controls, col_plot = st.columns([1, 3])

with col_controls:
    st.subheader("Filters")
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

    x_indicator = st.selectbox("X-axis Indicator", available_indicators, index=0, key="x_ind")
    y_indicator = st.selectbox("Y-axis Indicator", available_indicators, index=1, key="y_ind")

with col_plot:
    filtered = year_data[year_data['country'].isin(selected_countries)]
    pivot = filtered.pivot(index="country", columns="indicator", values="value").reset_index()

    if x_indicator in pivot.columns and y_indicator in pivot.columns:
        st.markdown("### Axis Scale Settings")
        col_x, col_y = st.columns(2)
        with col_x:
            x_scale = st.radio("X-axis Scale", ["Linear", "Logarithmic"], horizontal=True, key="x_scale")
        with col_y:
            y_scale = st.radio("Y-axis Scale", ["Linear", "Logarithmic"], horizontal=True, key="y_scale")

        log_x = (x_scale == "Logarithmic")
        log_y = (y_scale == "Logarithmic")

        fig = px.scatter(
            pivot,
            x=x_indicator,
            y=y_indicator,
            text="country",
            title=f"{y_indicator} vs {x_indicator} in {selected_year}",
            height=600,
            log_x=log_x,
            log_y=log_y
        )
        fig.update_traces(marker=dict(size=12), textposition="top center")
        fig.update_layout(
            plot_bgcolor='#222222',
            paper_bgcolor='#222222',
            font=dict(color='white'),
            xaxis=dict(showgrid=True, gridcolor='#444444', zerolinecolor='#666666'),
            yaxis=dict(showgrid=True, gridcolor='#444444', zerolinecolor='#666666'),
            title_font=dict(color='white'),
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("One or both selected indicators are not available for the chosen countries and year.")
