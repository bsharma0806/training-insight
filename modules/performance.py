def display(data):
    import streamlit as st
    import pandas as pd
    import numpy as np

    st.subheader("⚡ Performance Profile")

    # 1. Parse time and required fields
    if 'timestamp' in data.columns:
        data['time'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'])
    else:
        st.error("No timestamp or time column found.")
        return

    data = data.sort_values('time').reset_index(drop=True)
    data['elapsed_sec'] = (data['time'] - data['time'].iloc[0]).dt.total_seconds()

    # 2. Compute necessary columns: cadence, power, speed (km/h), HR efficiency, grade
    if 'cadence' in data.columns:
        avg_cadence = data['cadence'].mean()
        st.metric("Avg Cadence (spm)", f"{avg_cadence:.1f}")
    else:
        st.write("No cadence data available.")

    # Power: use existing or model if 'power' not present
    if 'power' in data.columns:
        avg_power = data['power'].mean()
        st.metric("Avg Power (W)", f"{avg_power:.1f}")
    else:
        # Basic modeled power approximation using speed^3 (assumes constant coefficient)
        if 'distance' in data.columns:
            time_diff = data['time'].diff().dt.total_seconds().fillna(0)
            speed_m_s = data['distance'].diff().fillna(0).div(time_diff.replace(0, np.nan))
            # simple cubic model (coefficient arbitrary, just for relative scaling)
            data['modeled_power'] = (speed_m_s ** 3).fillna(0)
            avg_power = data['modeled_power'].mean()
            st.metric("Modeled Power (arb units)", f"{avg_power:.1f}")
        else:
            st.write("No distance data to model power.")

    # Speed (km/h) for HR efficiency and stability
    if 'distance' in data.columns:
        time_diff = data['time'].diff().dt.total_seconds().fillna(0)
        data['speed_kmh'] = (data['distance'].diff().fillna(0).div(time_diff.replace(0, np.nan))) * 3.6
    else:
        data['speed_kmh'] = np.nan

    if 'heart_rate' in data.columns and 'speed_kmh' in data.columns:
        data['hr_efficiency'] = data['speed_kmh'].div(data['heart_rate'].replace(0, np.nan)).fillna(0)
        avg_eff = data['hr_efficiency'].mean()
        st.metric("Avg HR Efficiency (km/h per bpm)", f"{avg_eff:.3f}")
    else:
        st.write("Insufficient data for HR efficiency.")

    # 3. Stability scores: variance of cadence, power, HR, speed
    stability = {}
    if 'cadence' in data.columns:
        stability['Cadence'] = data['cadence'].var()
    if 'heart_rate' in data.columns:
        stability['Heart Rate'] = data['heart_rate'].var()
    if 'speed_kmh' in data.columns:
        stability['Speed'] = data['speed_kmh'].var()
    if 'power' in data.columns or 'modeled_power' in data.columns:
        power_col = 'power' if 'power' in data.columns else 'modeled_power'
        stability['Power'] = data[power_col].var()

    if stability:
        st.write("**Stability Scores (variance):**")
        st.dataframe(pd.Series(stability).rename("Variance").round(2))
    else:
        st.write("No data available for stability scores.")

    # 4. Context-sensitive performance profiles using time-integrated lens
    st.markdown("**📈 Time-Integrated Performance Comparison**")

    n = len(data)
    if n < 3:
        st.write("Not enough data for deeper analysis.")
        return

    # First vs Last Third
    thirds = np.array_split(data, 3)
    metrics = {}
    # Choose metrics to compare: HR efficiency and speed
    for idx, seg in enumerate(['First Third', 'Middle Third', 'Last Third']):
        seg_data = thirds[idx]
        metrics[seg] = {
            'Avg Speed (km/h)': seg_data['speed_kmh'].mean() if 'speed_kmh' in seg_data else np.nan,
            'Avg HR Efficiency': seg_data['hr_efficiency'].mean() if 'hr_efficiency' in seg_data else np.nan,
            'Avg Cadence': seg_data['cadence'].mean() if 'cadence' in seg_data else np.nan,
        }
    st.write("**Performance by Thirds:**")
    st.dataframe(pd.DataFrame(metrics).T.round(2))

    # Efficiency Drop: compare first vs last third
    if 'hr_efficiency' in data.columns:
        drop = metrics['First Third']['Avg HR Efficiency'] - metrics['Last Third']['Avg HR Efficiency']
        st.write(f"🚩 **Efficiency Drop (first vs last third):** {drop:.3f} km/h per bpm")

    # Early vs Late Climbs: define climbs where grade > 1%
    if 'enhanced_altitude' in data.columns and 'distance' in data.columns:
        elev_diff = data['enhanced_altitude'].diff().fillna(0)
        dist_m = data['distance'].diff().fillna(0)
        data['grade_pct'] = elev_diff.div(dist_m.replace(0, np.nan)) * 100
        climbs = data[data['grade_pct'] > 1]  # early threshold
        halfway = data['elapsed_sec'].iloc[-1] / 2
        early_climbs = climbs[climbs['elapsed_sec'] <= halfway]
        late_climbs = climbs[climbs['elapsed_sec'] > halfway]
        if not early_climbs.empty and not late_climbs.empty:
            st.write("**Early vs Late Climbs Comparison:**")
            climb_metrics = {
                'Segment': ['Early Climbs', 'Late Climbs'],
                'Avg HR (bpm)': [early_climbs['heart_rate'].mean(), late_climbs['heart_rate'].mean()],
                'Avg Cadence': [early_climbs['cadence'].mean(), late_climbs['cadence'].mean()],
                'Avg Speed (km/h)': [early_climbs['speed_kmh'].mean(), late_climbs['speed_kmh'].mean()]
            }
            st.dataframe(pd.DataFrame(climb_metrics).round(2))
        else:
            st.write("Insufficient climb data for early/late comparison.")

    # 5. Best performance segment: find top 5% speed window
    if 'speed_kmh' in data.columns:
        threshold = data['speed_kmh'].quantile(0.95)
        best_seg = data[data['speed_kmh'] >= threshold]
        avg_time = best_seg['elapsed_sec'].mean() / 60  # in minutes
        st.write(f"🏅 **Best Performance Window (Top 5% speed):** around {avg_time:.1f} min")