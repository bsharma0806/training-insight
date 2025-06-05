def display(data):
    import streamlit as st
    import pandas as pd
    import plotly.express as px

    st.subheader("🗺 Terrain-Based Performance")

    if 'elevation' not in data.columns:
        st.warning("Elevation data required.")
        return

    data['elev_change'] = data['elevation'].diff().fillna(0)
    data['terrain'] = data['elev_change'].apply(lambda x: 'Climb' if x > 0.3 else 'Descent' if x < -0.3 else 'Flat')

    if 'heart_rate' in data.columns:
        summary = data.groupby('terrain')['heart_rate'].mean().rename("Avg HR")
        st.write("**Avg Heart Rate by Terrain Type:**")
        st.dataframe(summary.round(1))

    terrain_counts = data['terrain'].value_counts()
    fig = px.bar(terrain_counts, labels={'index': 'Terrain', 'value': 'Samples'}, title="Terrain Distribution")
    st.plotly_chart(fig)
