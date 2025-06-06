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
        st.error("No 'timestamp' or 'time' column found.")
        return

    data = data.sort_values('time').reset_index(drop=True)
    data['elapsed_min'] = (data['time'] - data['time'].iloc[0]).dt.total_seconds() / 60

    # 2. Compute raw pace (sec per km)
    if 'distance' in data.columns:
        time_diff = data['time'].diff().dt.total_seconds().fillna(0)
        dist_km = data['distance'].diff().fillna(0) / 1000.0
        raw_pace = time_diff.div(dist_km.replace(0, np.nan))
        data['pace_sec_per_km'] = raw_pace.fillna(method='ffill').fillna(0)
    else:
        st.error("No 'distance' column found for pace calculation.")
        return

    # 3. Ensure elevation data exists
    if 'enhanced_altitude' not in data.columns:
        st.error("No 'enhanced_altitude' column found for elevation.")
        return

    # 4. Verify heart rate exists
    if 'heart_rate' not in data.columns:
        st.error("No 'heart_rate' column found.")
        return

    # 5. Clean NaNs or infinite values in required columns
    required_cols = ['heart_rate', 'pace_sec_per_km', 'enhanced_altitude', 'elapsed_min']
    data[required_cols] = data[required_cols].replace([np.inf, -np.inf], np.nan)
    clean = data.dropna(subset=required_cols).copy()

    if clean.empty:
        st.error("No valid data to plot after cleaning.")
        return

    # 6. Build 3D bubble scatter: X=HR, Y=Pace, Z=Elevation, color=Time
    fig = px.scatter_3d(
        data_frame=clean,
        x='heart_rate',
        y='pace_sec_per_km',
        z='enhanced_altitude',
        color='elapsed_min',
        labels={
            'heart_rate': 'Heart Rate (bpm)',
            'pace_sec_per_km': 'Pace (sec/km)',
            'enhanced_altitude': 'Elevation (m)',
            'elapsed_min': 'Time (min)'
        },
        color_continuous_scale='Viridis',
        title='Performance: HR vs Pace vs Elevation'
    )

    # 7. Use a small uniform bubble size
    fig.update_traces(
        marker=dict(
            size=3,
            opacity=0.7,
            symbol='circle'
        )
    )

    st.plotly_chart(fig, use_container_width=True)
