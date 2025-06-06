import streamlit as st
from parsers.utils import parse_file
from modules import performance, summary, pacing, time_in_zone, terrain, heatmap, simulator

st.set_page_config(page_title="Training File Insight Engine", layout="wide")
st.title("🏃 Training File Insight Engine")

uploaded_file = st.file_uploader("Upload a .FIT, .TCX, or .GPX file", type=["fit", "tcx", "gpx"])

if uploaded_file:
    data = parse_file(uploaded_file)

    if data is None or data.empty:
        st.error("Unsupported file or empty dataset.")
    else:
        # Debug: show columns detected
        st.write("**Detected columns:**", list(data.columns))

        # Call performance first
        performance.display(data)

        # Other modules
        summary.display(data)
        pacing.display(data)
        time_in_zone.display(data)
        terrain.display(data)
        heatmap.display(data)
        simulator.display(data)
else:
    st.info("Upload a training file to get started.")
