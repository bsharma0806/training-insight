def display(data):
    import streamlit as st
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    st.subheader("🔥 Effort Distribution Heatmaps")

    if 'timestamp' in data.columns:
        data['time'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'])
    else:
        st.warning("No timestamp or time column found.")
        return

    if 'heart_rate' in data.columns and 'cadence' in data.columns and 'distance' in data.columns:
        data['speed_kmh'] = (data['distance'].diff().fillna(0) / data['time'].diff().dt.total_seconds()) * 3.6

        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        sns.kdeplot(x=data['heart_rate'], y=data['cadence'], fill=True, ax=axs[0])
        axs[0].set_title("HR vs Cadence")
        axs[0].set_xlabel("Heart Rate")
        axs[0].set_ylabel("Cadence")

        sns.kdeplot(x=data['heart_rate'], y=data['speed_kmh'], fill=True, ax=axs[1])
        axs[1].set_title("HR vs Speed (km/h)")
        axs[1].set_xlabel("Heart Rate")
        axs[1].set_ylabel("Speed (km/h)")

        st.pyplot(fig)
