def display(data):
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go

    st.subheader("🏃 Pacing & Fueling Breakdown (Enhanced)")

    # 1. Parse time
    if 'timestamp' in data.columns:
        data['time'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'])
    else:
        st.warning("No timestamp or time column found.")
        return

    # 2. Verify required fields
    if 'distance' not in data.columns:
        st.warning("Distance data required for pace calculations.")
        return
    if 'enhanced_altitude' not in data.columns:
        st.warning("Enhanced altitude data required for elevation plots.")
        return
    if 'heart_rate' not in data.columns:
        st.warning("Heart rate data required for HR plots.")
        return

    # 3. Sort and compute elapsed time in minutes
    data = data.sort_values('time').reset_index(drop=True)
    data['elapsed_min'] = (data['time'] - data['time'].iloc[0]).dt.total_seconds() / 60

    # 4. Compute raw pace (sec per km), then smooth it (rolling window of 5 samples)
    dist_km = data['distance'].diff().fillna(0) / 1000.0
    time_diff = data['time'].diff().dt.total_seconds().fillna(0)
    raw_pace = time_diff.div(dist_km.replace(0, np.nan))
    data['pace_sec_per_km'] = raw_pace.rolling(window=5, min_periods=1, center=True).mean().fillna(0)

    # 5. Compute grade percent (elevation percent)
    elev_diff = data['enhanced_altitude'].diff().fillna(0)
    dist_m = data['distance'].diff().fillna(0)
    data['grade_pct'] = (elev_diff.div(dist_m.replace(0, np.nan)) * 100).fillna(0)

    # 6. Assign HR zones (COROS 6-zone model)
    bins = [0, 102, 120, 138, 156, 174, 300]
    labels = ['Z1 Recovery', 'Z2 Endurance', 'Z3 Tempo', 'Z4 Threshold', 'Z5 VO2 Max', 'Z6 Anaerobic']
    data['hr_zone'] = pd.cut(data['heart_rate'], bins=bins, labels=labels, right=False)

    # 7. Define colors for each zone
    zone_colors = {
        'Z1 Recovery': 'blue',
        'Z2 Endurance': 'green',
        'Z3 Tempo': 'orange',
        'Z4 Threshold': 'red',
        'Z5 VO2 Max': 'purple',
        'Z6 Anaerobic': 'black'
    }

    # 8. Build a Plotly figure: no connecting lines across different HR zones
    fig = go.Figure()
    # Create a 'segment' column that increments whenever HR zone changes
    data['segment'] = (data['hr_zone'] != data['hr_zone'].shift(1)).cumsum()
    for seg_id, seg_df in data.groupby('segment'):
        zone = seg_df['hr_zone'].iloc[0]
        if pd.isna(zone):
            continue
        fig.add_trace(
            go.Scatter(
                x=seg_df['elapsed_min'],
                y=seg_df['heart_rate'],
                mode='lines',
                name=f"HR {zone}",
                line=dict(color=zone_colors.get(zone, 'gray'))
            )
        )

    # 9. Checkbox to display smoothed pace
    show_pace = st.checkbox("Show Smoothed Pace (sec/km)", value=False)
    if show_pace:
        fig.add_trace(
            go.Scatter(
                x=data['elapsed_min'],
                y=data['pace_sec_per_km'],
                mode='lines',
                name='Pace (sec/km)',
                line=dict(color='royalblue', dash='dash'),
                yaxis='y2'
            )
        )
        fig.update_layout(
            yaxis2=dict(
                title="Pace (sec/km)",
                overlaying='y',
                side='right'
            )
        )

    # 10. Checkbox to display grade percentage
    show_elev = st.checkbox("Show Grade (%)", value=False)
    if show_elev:
        fig.add_trace(
            go.Scatter(
                x=data['elapsed_min'],
                y=data['grade_pct'],
                mode='lines',
                name='Grade (%)',
                line=dict(color='green', dash='dot'),
                yaxis='y3'
            )
        )
        fig.update_layout(
            yaxis3=dict(
                title="Grade (%)",
                anchor='free',
                overlaying='y',
                side='right',
                position=0.95
            )
        )

    fig.update_layout(
        title="Heart Rate Over Time (Colored by HR Zone)",
        xaxis_title="Time (min)",
        yaxis_title="Heart Rate (bpm)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # 11. Filtering options
    st.markdown("**Filter Segments by Metric**")
    filter_metric = st.selectbox(
        "Select metric to filter by:",
        ["None", "Heart Rate (bpm)", "Pace (sec/km)", "Grade (%)"]
    )

    if filter_metric == "Heart Rate (bpm)":
        min_hr, max_hr = st.slider(
            "Select HR Range (bpm):",
            int(data['heart_rate'].min()), int(data['heart_rate'].max()),
            (int(data['heart_rate'].min()), int(data['heart_rate'].max()))
        )
        mask = data['heart_rate'].between(min_hr, max_hr)

    elif filter_metric == "Pace (sec/km)":
        min_pace, max_pace = st.slider(
            "Select Pace Range (sec/km):",
            float(data['pace_sec_per_km'].min()), float(data['pace_sec_per_km'].max()),
            (float(data['pace_sec_per_km'].min()), float(data['pace_sec_per_km'].max()))
        )
        mask = data['pace_sec_per_km'].between(min_pace, max_pace)

    elif filter_metric == "Grade (%)":
        min_grade, max_grade = st.slider(
            "Select Grade Range (%):",
            float(data['grade_pct'].min()), float(data['grade_pct'].max()),
            (float(data['grade_pct'].min()), float(data['grade_pct'].max()))
        )
        mask = data['grade_pct'].between(min_grade, max_grade)

    else:
        mask = pd.Series([True] * len(data))

    # 12. Plot filtered segments with same coloring
    if filter_metric != "None":
        filtered = data[mask]
        fig2 = go.Figure()
        for zone, color in zone_colors.items():
            zone_df = filtered[filtered['hr_zone'] == zone]
            if not zone_df.empty:
                fig2.add_trace(
                    go.Scatter(
                        x=zone_df['elapsed_min'],
                        y=zone_df['heart_rate'],
                        mode='markers',
                        name=f"HR {zone}",
                        marker=dict(color=color)
                    )
                )
        fig2.update_layout(
            title=f"Filtered Segments: {filter_metric}",
            xaxis_title="Time (min)",
            yaxis_title="Heart Rate (bpm)"
        )
        st.plotly_chart(fig2, use_container_width=True)
