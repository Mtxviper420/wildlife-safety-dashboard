import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

# Page Layout Configuration
st.set_page_config(
    page_title="Wildlife Highway Safety System", page_icon="🐘", layout="wide"
)

# Custom CSS for UI styling
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)


# Generate Realistic Mock Data for Interim Evaluation
@st.cache_data
def load_mock_data():
  np.random.seed(42)
  n = 60
  return pd.DataFrame({
      "timestamp": pd.date_range(
          start="2026-06-01 18:00:00", periods=n, freq="2h"
      ).strftime("%Y-%m-%d %H:%M:%S"),
      "species": np.random.choice(
          [
              "Elephant",
              "Wild boar",
              "Deer",
              "Indian Gaur",
              "Cow",
              "Leopard",
              "Dog",
          ],
          n,
          p=[0.15, 0.2, 0.2, 0.1, 0.15, 0.1, 0.1],
      ),
      "confidence": np.random.uniform(0.82, 0.98, n),
      "latitude": np.random.uniform(10.01, 10.15, n),
      "longitude": np.random.uniform(76.90, 77.05, n),
      "driver_requested": np.random.choice(
          [True, False], n, p=[0.7, 0.3]
      ),
      "deterrent_selected": np.random.choice(
          [
              "Acoustic Low-Frequency Buzz",
              "Strobe Light Array",
              "Buzzer + Strobe",
              "None (Driver Dismissed)",
          ],
          n,
      ),
      "status": "Logged & Transmitted",
  })


df = load_mock_data()

# Header Section
st.title("🛡️ ML-Based Driver-Controlled Wildlife Deterrent System")
st.markdown(
    "**Interim Project Prototype Dashboard** | Real-time vehicle telemetry,"
    " species detection logs, and highway crossing hotspots."
)
st.markdown("---")

# Sidebar Controls
st.sidebar.header("🔍 Evaluation Controls")
selected_species = st.sidebar.multiselect(
    "Filter Species Groups",
    options=df["species"].unique(),
    default=df["species"].unique(),
)
filtered_df = df[df["species"].isin(selected_species)]

# Top Metric Cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sightings Logged", len(filtered_df))
top_species = (
    filtered_df["species"].mode()[0] if not filtered_df.empty else "N/A"
)
c2.metric("Most Frequent Species", top_species)
driver_acts = (
    int(filtered_df["driver_requested"].sum())
    if not filtered_df.empty
    else 0
)
c3.metric("Driver Overrides / Actions", driver_acts)
avg_conf = (
    f"{filtered_df['confidence'].mean()*100:.1f}%"
    if not filtered_df.empty
    else "0%"
)
c4.metric("Avg AI Confidence", avg_conf)

st.markdown("---")

# Map and Heat Zones Section
st.subheader("🗺️ Highway Crossing Hotspots & Live Sighting Map")
if not filtered_df.empty:
  lat_center = filtered_df["latitude"].mean()
  lon_center = filtered_df["longitude"].mean()

  heatmap_layer = pdk.Layer(
      "HexagonLayer",
      data=filtered_df,
      get_position=["longitude", "latitude"],
      radius=180,
      elevation_scale=40,
      elevation_range=[0, 1000],
      pickable=True,
      extruded=True,
  )

  scatter_layer = pdk.Layer(
      "ScatterplotLayer",
      data=filtered_df,
      get_position=["longitude", "latitude"],
      get_color="[255, 69, 0, 180]",
      get_radius=80,
      pickable=True,
      auto_highlight=True,
  )

  view_state = pdk.ViewState(
      latitude=lat_center, longitude=lon_center, zoom=12, pitch=45
  )

  r = pdk.Deck(
      layers=[heatmap_layer, scatter_layer],
      initial_view_state=view_state,
      tooltip={
          "html": "<b>Species:</b> {species} <br> <b>Confidence:</b>"
          " {confidence} <br> <b>Time:</b> {timestamp}"
      },
  )
  st.pydeck_chart(r)
else:
  st.warning("Please select at least one species from the sidebar.")

st.markdown("---")

# Analytics Charts
col_left, col_right = st.columns(2)
with col_left:
  st.subheader("📊 Sighting Frequency per Species")
  if not filtered_df.empty:
    st.bar_chart(filtered_df["species"].value_counts())

with col_right:
  st.subheader("⚙️ Deterrent Activation Distribution")
  if not filtered_df.empty:
    st.bar_chart(filtered_df["deterrent_selected"].value_counts())

st.markdown("---")

# Live Telemetry Log Table
st.subheader("📋 Central Database Telemetry Logs")
st.dataframe(filtered_df, use_container_width=True)