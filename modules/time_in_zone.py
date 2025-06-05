def display(data):
    import streamlit as st
    import pandas as pd

    st.subheader("⏳ Time-in-Zone + Efficiency")

    if 'heart_rate' not in data.columns:
        st.warning("Heart rate data required.")
        return

    # COROS 6-zone system
    bins = [0, 102, 120, 138, 156, 174, 300]
    labels = ['Z1 Recovery', 'Z2 Endurance', 'Z3 Tempo', 'Z4 Threshold', 'Z5 VO2 Max', 'Z6 Anaerobic']
    data['hr_zone'] = pd.cut(data['heart_rate'], bins=bins, labels=labels, right=False)

    zone_counts = data['hr_zone'].value_counts().sort_index()
    st.bar_chart(zone_counts)

    if 'distance' in data.columns:
        data['speed'] = data['distance'].diff().fillna(0)
        data['hr_eff'] = data['speed'] / data['heart_rate']
        data['rei'] = data['speed'] / data['heart_rate']
        data['ces'] = data['speed'] / data['heart_rate'] / (data['speed'].count() / 60)

        eff = data.groupby('hr_zone').agg({
            'hr_eff': 'mean',
            'rei': 'mean',
            'ces': 'mean'
        }).round(3)
        st.write("**Efficiency Metrics by Zone:**")
        st.dataframe(eff)
