def display(data):
    import streamlit as st
    import pandas as pd

    st.subheader("📊 File Summary")
    if 'timestamp' in data.columns:
        data['time'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'])
    else:
        st.error("No timestamp or time column found in this file.")
        return

    data = data.sort_values('time')
    duration_sec = (data['time'].iloc[-1] - data['time'].iloc[0]).total_seconds()
    minutes, seconds = divmod(duration_sec, 60)
    st.metric("Duration", f"{int(minutes)} min {int(seconds):02d} sec")

    if 'distance' in data.columns:
        total_distance = data['distance'].dropna().max() / 1000
        st.metric("Total Distance (km)", f"{total_distance:.2f}")
    if 'enhanced_altitude' in data.columns:
        total_elev = data['enhanced_altitude'].diff().clip(lower=0).sum()
        st.metric("Elevation Gain (m)", f"{total_elev:.0f}")
    if 'heart_rate' in data.columns:
        avg_hr = data['heart_rate'].mean()
        st.metric("Avg HR (bpm)", f"{avg_hr:.0f}")
    if 'cadence' in data.columns:
        avg_cad = data['cadence'].mean()
        st.metric("Avg Cadence", f"{avg_cad:.0f}")
