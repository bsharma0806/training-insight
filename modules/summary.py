def display(data):
    import streamlit as st
    import pandas as pd

    st.subheader("📊 File Summary")
    data['time'] = pd.to_datetime(data['time'])
    data = data.sort_values('time')
    duration = (data['time'].iloc[-1] - data['time'].iloc[0]).total_seconds() / 60

    st.metric("Duration (min)", f"{duration:.1f}")
    if 'distance' in data.columns:
        total_distance = data['distance'].dropna().max() / 1000
        st.metric("Total Distance (km)", f"{total_distance:.2f}")
    if 'elevation' in data.columns:
        total_elev = data['elevation'].diff().clip(lower=0).sum()
        st.metric("Elevation Gain (m)", f"{total_elev:.0f}")
    if 'heart_rate' in data.columns:
        avg_hr = data['heart_rate'].mean()
        st.metric("Avg HR (bpm)", f"{avg_hr:.0f}")
    if 'cadence' in data.columns:
        avg_cad = data['cadence'].mean()
        st.metric("Avg Cadence", f"{avg_cad:.0f}")
