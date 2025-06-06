def display(data):
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px

    st.subheader("🔬 Performance 3D Scatter")

    # 1. Parse time
    if 'timestamp' in data.columns:
        data['time'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'])
    else:
        st.error("No timestamp or time column found.")
        return

    data = data.sort_values('time').reset_index(drop=True)
    data['elapsed_min'] = (data['time'] - data['time'].iloc[0]).dt.total_seconds() / 60

    # 2. Compute speed (km/h)
    if 'distance' in data.columns:
        time_diff = data['time'].diff().dt.total_seconds().fillna(0)
        data['speed_kmh'] = (
            data['distance']
            .diff()
            .fillna(0)
            .div(time_diff.replace(0, np.nan))
        ) * 3.6
    else:
        st.error("Distance data required for speed calculation.")
        return

    # 3. Ensure elevation data exists
    if 'enhanced_altitude' not in data.columns:
        st.error("Enhanced altitude data required for elevation axis.")
        return

    # 4. Verify heart rate exists
    if 'heart_rate' not in data.columns:
        st.error("Heart rate data required.")
        return

    # 5. Clean NaNs or infinities
    required_cols = ['speed_kmh', 'heart_rate', 'enhanced_altitude', 'elapsed_min']
    data[required_cols] = data[required_cols].replace([np.inf, -np.inf], np.nan)
    clean = data.dropna(subset=required_cols).copy()

    if clean.empty:
        st.error("No valid data points to plot after cleaning.")
        return

    # 6. Build 3D bubble scatter: X = speed_kmh, Y = heart_rate, Z = enhanced_altitude, color = elapsed_min
    fig = px.scatter_3d(
        data_frame=clean,
        x='speed_kmh',
        y='heart_rate',
        z='enhanced_altitude',
        color='elapsed_min',
        labels={
            'speed_kmh': 'Speed (km/h)',
            'heart_rate': 'Heart Rate (bpm)',
            'enhanced_altitude': 'Elevation (m)',
            'elapsed_min': 'Time (min)'
        },
        color_continuous_scale='Viridis',
        title='Performance Clusters: Speed vs HR vs Elevation'
    )

    # 7. Use small uniform bubble size (circle markers)
    fig.update_traces(
        marker=dict(
            size=4,
            symbol='circle',
            opacity=0.7
        )
    )

    st.plotly_chart(fig, use_container_width=True)