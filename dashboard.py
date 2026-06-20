import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="F1 Strategy Control Room",
    layout="wide"
)

st.title("🏎️ F1 Strategy Control Room")

# =====================================
# LOAD DATA
# =====================================

@st.cache_data
def load_results():
    return pd.read_csv("data/strategy_results.csv")

@st.cache_data
def load_features():
    return pd.read_csv("data/feature_dataset.csv")

results_df = load_results()
features_df = load_features()

# Map encoded drivers → names
driver_map = (
    features_df[["DriverEncoded","Driver"]]
    .drop_duplicates()
    .set_index("DriverEncoded")["Driver"]
    .to_dict()
)

results_df["Driver"] = results_df["DriverEncoded"].map(driver_map)

# =====================================
# SIDEBAR CONTROLS
# =====================================

st.sidebar.header("Simulation Controls")

strategies = sorted(results_df["strategy"].unique())
drivers = sorted(results_df["Driver"].unique())

selected_strategy = st.sidebar.selectbox(
    "Strategy",
    strategies
)

selected_driver = st.sidebar.selectbox(
    "Driver",
    drivers
)

strategy_df = results_df[
    results_df["strategy"] == selected_strategy
]

driver_df = strategy_df[
    strategy_df["Driver"] == selected_driver
]

N_SIMULATIONS = strategy_df["simulation"].nunique()

st.sidebar.write(f"Simulations: {N_SIMULATIONS}")

# =====================================
# METRICS PANEL
# =====================================

wins = driver_df[driver_df["Position"] == 1]
win_prob = wins["simulation"].nunique() / N_SIMULATIONS

podiums = driver_df[driver_df["Position"] <= 3]
podium_prob = podiums["simulation"].nunique() / N_SIMULATIONS

avg_position = driver_df["Position"].mean()
avg_time = driver_df["cumulative_time"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Win Probability", f"{win_prob*100:.1f}%")
col2.metric("Podium Probability", f"{podium_prob*100:.1f}%")
col3.metric("Average Finish", f"{avg_position:.2f}")
col4.metric("Avg Race Time", f"{avg_time:.0f}s")

st.divider()

# =====================================
# STRATEGY LEADERBOARD
# =====================================

st.subheader("Strategy Leaderboard")

summary = results_df.groupby("strategy").apply(
    lambda x: pd.Series({
        "win_prob": (x["Position"] == 1).sum() / x["simulation"].nunique(),
        "podium_prob": (x["Position"] <= 3).sum() / x["simulation"].nunique(),
        "avg_position": x["Position"].mean(),
        "avg_race_time": x["cumulative_time"].mean()
    })
)

st.dataframe(summary)

# =====================================
# STRATEGY PERFORMANCE CHART
# =====================================

st.subheader("Strategy Win Probability")

fig1 = px.bar(
    summary,
    x=summary.index,
    y="win_prob",
    title="Win Probability by Strategy",
    color="win_prob",
)

st.plotly_chart(fig1, use_container_width=True)

# =====================================
# POSITION DISTRIBUTION
# =====================================

st.subheader("Finish Position Distribution")

fig2 = px.histogram(
    driver_df,
    x="Position",
    nbins=20,
    title="Finish Position Distribution"
)

st.plotly_chart(fig2, use_container_width=True)

# =====================================
# POSITION TIMELINE
# =====================================

if "LapNumber" in results_df.columns:

    st.subheader("Race Position Timeline")

    timeline = results_df[
        results_df["strategy"] == selected_strategy
    ]

    fig3 = px.line(
        timeline,
        x="LapNumber",
        y="Position",
        color="Driver",
        title="Driver Position Over Race"
    )

    fig3.update_yaxes(autorange="reversed")

    st.plotly_chart(fig3, use_container_width=True)

# =====================================
# GAP TO LEADER
# =====================================

st.subheader("Gap to Leader Analysis")

gap_df = strategy_df.copy()

leader_time = gap_df.groupby("simulation")["cumulative_time"].transform("min")
gap_df["gap_to_leader"] = gap_df["cumulative_time"] - leader_time

driver_gap = gap_df[
    gap_df["Driver"] == selected_driver
]

fig4 = px.box(
    driver_gap,
    y="gap_to_leader",
    title="Gap to Leader Distribution"
)

st.plotly_chart(fig4, use_container_width=True)

# =====================================
# RACE REPLAY ANIMATION
# =====================================

st.subheader("Race Replay")

if "LapNumber" in results_df.columns:

    replay_df = results_df[
        results_df["strategy"] == selected_strategy
    ]

    replay_df = replay_df.sort_values(["LapNumber","Position"])

    fig_replay = px.scatter(
        replay_df,
        x="Position",
        y="Driver",
        animation_frame="LapNumber",
        color="Driver",
        title="Race Replay",
        range_x=[1,25]
    )

    fig_replay.update_layout(
        xaxis_title="Position",
        yaxis_title="Driver"
    )

    st.plotly_chart(fig_replay, use_container_width=True)

# =====================================
# LAP LEADERBOARD
# =====================================

st.subheader("Lap Leaderboard")

if "LapNumber" in results_df.columns:

    lap_select = st.slider(
        "Select Lap",
        int(results_df["LapNumber"].min()),
        int(results_df["LapNumber"].max()),
        1
    )

    lap_df = results_df[
        (results_df["LapNumber"] == lap_select) &
        (results_df["strategy"] == selected_strategy)
    ]

    lap_df = lap_df.sort_values("Position")

    st.dataframe(
        lap_df[["Driver","Position","cumulative_time"]]
    )