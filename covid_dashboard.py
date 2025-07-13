import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

st.set_page_config(page_title="Global COVID-19 Dashboard", layout="wide")
st.title("🌍 Global COVID-19 Pandemic Dashboard")
st.markdown("Real-time global visualizations of the COVID-19 pandemic and its impacts.")

@st.cache_data
def load_data():
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    df = pd.read_csv(url, parse_dates=['date'])
    return df

df = load_data()
st.sidebar.header("Dashboard Controls")
countries = df['location'].unique()
selected_countries = st.sidebar.multiselect("Select Countries:", countries, default=["India", "United States"])
metrics = ["total_cases", "total_deaths", "total_vaccinations"]
selected_metric = st.sidebar.selectbox("Select Metric:", metrics)
filtered_df = df[df['location'].isin(selected_countries)]

col1, col2 = st.columns(2)
with col1:
    st.subheader(f"📈 {selected_metric.replace('_', ' ').title()} Over Time")
    fig = px.line(filtered_df, x='date', y=selected_metric, color='location',
                  labels={'date': 'Date', selected_metric: selected_metric.replace('_', ' ').title()})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🗺 Global Map (Latest Data)")
    latest = df[df['date'] == df['date'].max()]
    world_map = latest[latest['location'].isin(selected_countries)]
    map_fig = px.choropleth(world_map, locations="location", locationmode="country names",
                            color=selected_metric, hover_name="location",
                            color_continuous_scale="Reds", title=f"{selected_metric.replace('_', ' ').title()} by Country")
    st.plotly_chart(map_fig, use_container_width=True)

st.subheader("📊 Summary Table (Latest)")
latest_stats = filtered_df.sort_values('date').groupby('location').tail(1)
st.dataframe(latest_stats[['location', 'total_cases', 'total_deaths', 'total_vaccinations']].set_index('location'))

csv = latest_stats.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Latest Data (CSV)", csv, "covid_summary.csv", "text/csv")

st.subheader("💉 Vaccination Comparison")
vax_fig = px.bar(latest_stats, x='location', y='total_vaccinations', color='location')
st.plotly_chart(vax_fig, use_container_width=True)

st.subheader("💼 Economic Impact (Mock Data)")
mock_data = pd.DataFrame({
    'Country': selected_countries,
    'GDP Change (%)': [-6.7, -3.4][:len(selected_countries)],
    'Unemployment Rate (%)': [8.5, 6.2][:len(selected_countries)],
})
st.dataframe(mock_data.set_index("Country"))
eco_fig = px.bar(mock_data, x='Country', y='GDP Change (%)', color='Country', title='Estimated GDP Decline due to COVID-19')
st.plotly_chart(eco_fig, use_container_width=True)

st.subheader("📸 Export Chart Image")
buffer = BytesIO()
fig.write_image(buffer, format="png")
st.download_button("⬇️ Download Line Chart as PNG", buffer.getvalue(), file_name="covid_chart.png")

st.markdown("---")
st.caption("Data Source: Our World in Data | Demo Economic Data is illustrative only.")