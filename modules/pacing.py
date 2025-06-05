def display(data):
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    st.subheader("🏃 Pacing & Fueling Breakdown (Enhanced)")

    # Ensure time is parsed
    if 'timestamp' in data.columns:
        data['time'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'])
    else:
        st.warning("No timestamp or time column found.")
        return

    # Ensure necessary fields exist
    if 'distance' not in data.columns:
        st.warning("Distance data required for pace calculations.")
        return
    if 'enhanced_altitude' not in data.columns:
        st.warning("Enhanced altitude data required for elevation plots.")
        return
    if 'heart_rate' not in data.columns:
        st.warning("Heart rate data required for HR plots.")
        return

    # Sort by time and compute elapsed seconds
    data = data.sort_values('time').reset_index(drop=True)
    data['elapsed'] = (data['time'] - data['time'].iloc[0]).dt.total_seconds()

    # Compute pace (sec per km)
    dist_km = data['distance'].diff().fillna(0) / 1000.0
    time_diff = data['time'].diff().dt.total_seconds().fillna(0)
    # Avoid division by zero
    data['pace_sec_per_km'] = time_diff.div(dist_km.replace(0, pd.NA)).fillna(method='ffill').fillna(0)

    # Convert to min/km string for display
    data['pace_min_km'] = data['pace_sec_per_km'].apply(
        lambda x: f"{int(x//60)}:{int(x%60):02d}" if x > 0 else "0:00"
    )

    # Compute incline (m/s) = altitude diff / time diff
    elev_diff = data['enhanced_altitude'].diff().fillna(0)
    data['incline_m_per_s'] = elev_diff.div(time_diff.replace(0, pd.NA)).fillna(0)

    # HR zones definition (COROS 6-zone model)
    bins = [0, 102, 120, 138, 156, 174, 300]
    labels = ['Z1 Recovery', 'Z2 Endurance', 'Z3 Tempo', 'Z4 Threshold', 'Z5 VO2 Max', 'Z6 Anaerobic']
    data['hr_zone'] = pd.cut(data['heart_rate'], bins=bins, labels=labels, right=False)

    # Plot checkboxes: pace and elevation
    show_pace = st.checkbox("Show Pace (min/km)", value=False)
    show_elev = st.checkbox("Show Elevation (m)", value=False)

    # Base figure: HR over time colored by zone
    fig = px.line(
        data,
        x='elapsed',
        y='heart_rate',
        color='hr_zone',
        labels={'elapsed': 'Time (sec)', 'heart_rate': 'Heart Rate (bpm)'},
        title="Heart Rate Over Time (Colored by HR Zone)",
        color_discrete_sequence=px.colors.qualitative.Set1
    )

    # Add pace trace if selected
    if show_pace:
        fig.add_trace(
            go.Scatter(
                x=data['elapsed'],
                y=data['pace_sec_per_km'],
                mode='lines',
                name='Pace (sec/km)',
                yaxis='y2',
                line=dict(color='royalblue', dash='dash')
            )
        )
        fig.update_layout(
            yaxis2=dict(
                title="Pace (sec/km)",
                overlaying='y',
                side='right'
            )
        )

    # Add elevation trace if selected
    if show_elev:
        fig.add_trace(
            go.Scatter(
                x=data['elapsed'],
                y=data['enhanced_altitude'],
                mode='lines',
                name='Elevation (m)',
                yaxis='y3',
                line=dict(color='green', dash='dot')
            )
        )
        fig.update_layout(
            yaxis3=dict(
                title="Elevation (m)",
                anchor='free',
                overlaying='y',
                side='right',
                position=0.95
            )
        )

    # Display the combined figure
    st.plotly_chart(fig, use_container_width=True)

    # Filtering options
    st.markdown("**Filter Segments by Metric**")
    filter_metric = st.selectbox(
        "Select metric to filter by:",
        ["None", "Heart Rate Zone", "Pace (sec/km)", "Incline (m/s)"]
    )

    if filter_metric == "Heart Rate Zone":
        selected_zones = st.multiselect("Choose HR Zones:", options=labels, default=labels)
        mask = data['hr_zone'].isin(selected_zones)

    elif filter_metric == "Pace (sec/km)":
        min_pace, max_pace = st.slider(
            "Select Pace Range (sec/km):",
            float(data['pace_sec_per_km'].min()),
            float(data['pace_sec_per_km'].max()),
            (float(data['pace_sec_per_km'].min()), float(data['pace_sec_per_km'].max()))
        )
        mask = data['pace_sec_per_km'].between(min_pace, max_pace)

    elif filter_metric == "Incline (m/s)":
        min_inc, max_inc = st.slider(
            "Select Incline Range (m/s):",
            float(data['incline_m_per_s'].min()),
            float(data['incline_m_per_s'].max()),
            (float(data['incline_m_per_s'].min()), float(data['incline_m_per_s'].max()))
        )
        mask = data['incline_m_per_s'].between(min_inc, max_inc)

    else:
        mask = pd.Series([True] * len(data))

    # Highlight filtered segments on a separate chart
    if filter_metric != "None":
        filtered = data[mask]
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=filtered['elapsed'],
                y=filtered['heart_rate'],
                mode='markers',
                marker=dict(color='red'),
                name='Filtered HR'
            )
        )
        fig2.update_layout(
            title=f"Filtered Segments: {filter_metric}",
            xaxis_title="Time (sec)",
            yaxis_title="Heart Rate (bpm)"
        )
        st.plotly_chart(fig2, use_container_width=True)
