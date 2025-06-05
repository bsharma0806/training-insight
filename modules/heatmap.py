def display(data):
    import streamlit as st
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    st.subheader("🔥 Effort Distribution Heatmaps")

    if 'heart_rate' in data.columns and 'cadence' in data.columns:
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        sns.kdeplot(x=data['heart_rate'], y=data['cadence'], fill=True, ax=axs[0])
        axs[0].set_title("HR vs Cadence")
        axs[0].set_xlabel("Heart Rate")
        axs[0].set_ylabel("Cadence")

        if 'distance' in data.columns:
            data['pace'] = data['distance'].diff().fillna(0)
            sns.kdeplot(x=data['heart_rate'], y=data['pace'], fill=True, ax=axs[1])
            axs[1].set_title("HR vs Pace")
            axs[1].set_xlabel("Heart Rate")
            axs[1].set_ylabel("Pace (m/s)")

        st.pyplot(fig)
