def display(data):
    import streamlit as st
    import plotly.graph_objects as go
    import pandas as pd

    st.subheader("🏃 Pacing & Fueling Breakdown")

    if 'timestamp' in data.columns:
        data['time'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'])
    else:
        st.warning("No timestamp or time column found.")
        return

    data = data.sort_values('time')
    data['elapsed'] = (data['time'] - data['time'].iloc[0]).dt.total_seconds()

    fig = go.Figure()
    if 'heart_rate' in data.columns:
        fig.add_trace(go.Scatter(x=data['elapsed']/60, y=data['heart_rate'], name="Heart Rate (bpm)", yaxis="y1"))
    if 'cadence' in data.columns:
        fig.add_trace(go.Scatter(x=data['elapsed']/60, y=data['cadence'], name="Cadence", yaxis="y2"))

    fig.update_layout(
        xaxis_title="Time (min)",
        yaxis=dict(title="HR", side="left"),
        yaxis2=dict(title="Cadence", overlaying='y', side="right"),
        legend=dict(x=0, y=1.1, orientation='h')
    )
    st.plotly_chart(fig, use_container_width=True)

    if 'heart_rate' in data.columns:
        rolling_hr = data['heart_rate'].rolling(window=10, min_periods=1).mean()
        peak_hr = rolling_hr.max()
        end_hr = rolling_hr.iloc[-1]
        if end_hr < peak_hr * 0.85:
            st.markdown("⚡ **Insight:** Significant HR fade detected in final 25% of session. Suggest earlier fueling or reduced early intensity.")
        else:
            st.markdown("✅ **Insight:** Heart rate remained stable — pacing was likely sustainable.")
