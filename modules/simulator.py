def display(data):
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go

    st.subheader("🔮 'What-If' Simulator")

    if 'timestamp' in data.columns:
        data['time'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'])
    else:
        st.warning("No timestamp or time column found.")
        return

    data = data.sort_values('time')
    data['elapsed'] = (data['time'] - data['time'].iloc[0]).dt.total_seconds()

    if 'heart_rate' not in data.columns or 'distance' not in data.columns:
        st.warning("Heart rate and distance data required.")
        return

    avg_hr = data['heart_rate'].mean()
    avg_pace = data['distance'].diff().mean()
    ideal_pace = [avg_pace for _ in range(len(data))]
    cumulative = pd.Series(ideal_pace).cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['elapsed']/60, y=data['distance'], name="Actual"))
    fig.add_trace(go.Scatter(x=data['elapsed']/60, y=cumulative, name="Simulated Even Pace"))
    fig.update_layout(title="What-If: Even Effort Pacing", xaxis_title="Time (min)", yaxis_title="Distance (m)")
    st.plotly_chart(fig)

    actual_total = data['distance'].iloc[-1]
    projected_time = data['elapsed'].iloc[-1] * (actual_total / cumulative.iloc[-1])
    st.markdown(f"**Projected Time (Even HR pacing):** {projected_time/60:.2f} min vs actual {data['elapsed'].iloc[-1]/60:.2f} min")
