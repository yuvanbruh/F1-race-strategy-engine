import pandas as pd
import json

# load dataset
# df = pd.read_csv("race_simulation_results.csv")
df = pd.read_csv("data/race_simulation_results.csv")

# keep only necessary columns
cols = [
    "DriverEncoded",
    "LapNumber",
    "lap_progress",
    "Position"
]

df = df[cols]

frames = []

# group by lap
for lap in sorted(df["LapNumber"].unique()):
    lap_data = df[df["LapNumber"] == lap]

    frame = {
        "lap": int(lap),
        "drivers": []
    }

    for _, row in lap_data.iterrows():
        frame["drivers"].append({
            "driver": int(row["DriverEncoded"]),
            "progress": float(row["lap_progress"]),
            "position": int(row["Position"])
        })

    frames.append(frame)

with open("race_replay.json", "w") as f:
    json.dump(frames, f)

print("Replay file created")