def display(data):
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px

    st.subheader("🔬 Performance 3D Scatter")

    # 1. Parse timestamp
    if 'timestamp' in data.columns:
        data['time'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'])
    else:
        st.error("No 'timestamp' or 'time' column found.")
        return

    data = data.sort_values('time').reset_index(drop=True)
    data['elapsed_min'] = (data['time'] - data['time'].iloc[0]).dt.total_seconds() / 60

    # 2. Compute pace (sec/km)
    if 'distance' in data.columns:
        time_diff = data['time'].diff().dt.total_seconds().fillna(0)
        dist_km = data['distance'].diff().fillna(0) / 1000.0
        data['pace_sec_per_km'] = time_diff.div(dist_km.replace(0, np.nan)).fillna(method='ffill').fillna(0)
    else:
        st.error("No 'distance' column found for pace calculation.")
        return

    # 3. Check elevation field
    if 'enhanced_altitude' not in data.columns:
        st.error("No 'enhanced_altitude' column found for elevation.")
        return

    # 4. Check heart rate
    if 'heart_rate' not in data.columns:
        st.error("No 'heart_rate' column found.")
        return

    # 5. Drop bad values
    required_cols = ['heart_rate', 'pace_sec_per_km', 'enhanced_altitude', 'elapsed_min']
    data[required_cols] = data[required_cols].replace([np.inf, -np.inf], np.nan)
    clean = data.dropna(subset=required_cols).copy()

    if clean.empty:
        st.error("No valid data to plot after cleaning.")
        return

    # 6. Create 3D scatter: X=HR, Y=Pace, Z=Elevation, color=Time
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

    # 7. Use uniformly small bubbles
    fig.update_traces(
        marker=dict(
            size=3,
            opacity=0.7,
            symbol='circle'
        )
    )

    st.plotly_chart(fig, use_container_width=True)
