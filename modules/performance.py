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
        data['speed_kmh'] = (data['distance'].diff().fillna(0).div(time_diff.replace(0, np.nan))) * 3.6
    else:
        st.error("Distance data required for speed calculation.")
        return

    # 3. Compute elevation grade (%)
    if 'enhanced_altitude' in data.columns:
        elev_diff = data['enhanced_altitude'].diff().fillna(0)
        dist_m = data['distance'].diff().fillna(0)
        data['grade_pct'] = (elev_diff.div(dist_m.replace(0, np.nan)) * 100).fillna(0)
    else:
        st.error("Enhanced altitude data required for grade calculation.")
        return

    # 4. Verify heart rate and cadence exist
    if 'heart_rate' not in data.columns:
        st.error("Heart rate data required.")
        return
    if 'cadence' not in data.columns:
        st.error("Cadence data required.")
        return

    # 5. Build 3D scatter: X = grade_pct, Y = speed_kmh, Z = heart_rate, size = cadence, color = elapsed_min
    fig = px.scatter_3d(
        data_frame=data,
        x='grade_pct',
        y='speed_kmh',
        z='heart_rate',
        size='cadence',
        color='elapsed_min',
        labels={
            'grade_pct': 'Grade (%)',
            'speed_kmh': 'Speed (km/h)',
            'heart_rate': 'Heart Rate (bpm)',
            'elapsed_min': 'Time (min)',
            'cadence': 'Cadence (spm)'
        },
        color_continuous_scale='Viridis',
        title='Performance Clusters: Grade vs Speed vs HR'
    )

    # Adjust marker sizing for better visualization
    fig.update_traces(
        marker=dict(
            sizemode='diameter',
            sizeref=2 * max(data['cadence']) / (40**2),
            opacity=0.7
        )
    )

    st.plotly_chart(fig, use_container_width=True)
