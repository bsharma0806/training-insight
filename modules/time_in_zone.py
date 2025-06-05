def display(data):
    import streamlit as st
    import pandas as pd
    import plotly.express as px

    st.subheader("⏳ Time-in-Zone + Efficiency")

    if 'heart_rate' not in data.columns:
        st.warning("Heart rate data required.")
        return

    bins = [0, 100, 120, 140, 160, 180, 300]
    labels = ['Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6']
    data['hr_zone'] = pd.cut(data['heart_rate'], bins=bins, labels=labels, right=False)
    zone_counts = data['hr_zone'].value_counts().sort_index()

    fig = px.bar(zone_counts, labels={'index': 'HR Zone', 'value': 'Time Points'}, title="Time in HR Zones")
    st.plotly_chart(fig)

    if 'distance' in data.columns:
        data['hr_eff'] = data['distance'].diff().fillna(0) / data['heart_rate']
        eff_by_zone = data.groupby('hr_zone')['hr_eff'].mean()
        st.write("**Efficiency per HR zone (meters per bpm):**")
        st.dataframe(eff_by_zone.round(2))
