from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import asyncio
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



feature_dataset = pd.read_csv("../data/feature_dataset.csv")
race_dataset = pd.read_csv("../data/race_dataset.csv")
simulation_results = pd.read_csv("../data/simulation_results.csv")
race_simulation_results = pd.read_csv("../data/race_simulation_results.csv")
monte_carlo_results = pd.read_csv("../data/monte_carlo_results.csv")
strategy_results = pd.read_csv("../data/strategy_results.csv")

drivers_list = race_simulation_results["DriverEncoded"].unique().tolist()



@app.get("/")
def home():
    return {"message": "F1 Control Room API"}



@app.get("/strategies")
def get_strategies():
    return strategy_results["strategy"].unique().tolist()


@app.get("/strategy_results")
def get_strategy_results():
    return strategy_results.to_dict(orient="records")


@app.get("/monte_carlo")
def get_monte_carlo():
    return monte_carlo_results.to_dict(orient="records")



@app.get("/laps")
def get_laps():
    return race_simulation_results.to_dict(orient="records")


@app.get("/laps/{lap}")
def get_lap(lap: int):
    df = race_simulation_results[race_simulation_results["LapNumber"] == lap]
    return df.to_dict(orient="records")


@app.get("/driver/{driver_id}")
def get_driver(driver_id: int):
    df = race_simulation_results[race_simulation_results["DriverEncoded"] == driver_id]
    return df.to_dict(orient="records")



@app.get("/race_dataset")
def get_race_dataset():
    return race_dataset.to_dict(orient="records")



@app.get("/feature_dataset")
def get_feature_dataset():
    return feature_dataset.to_dict(orient="records")



@app.get("/simulation_results")
def get_simulation_results():
    return simulation_results.to_dict(orient="records")


@app.get("/race_summary")
def race_summary():

    summary = race_simulation_results.groupby("DriverEncoded").agg(
        final_position=("Position", "last"),
        total_time=("cumulative_time", "last"),
        pit_stops=("pit_stop", "sum")
    )

    return summary.reset_index().to_dict(orient="records")



@app.websocket("/telemetry")
async def telemetry(ws: WebSocket):

    await ws.accept()

    positions = {d: random.random() for d in drivers_list}

    while True:

        for d in positions:
            positions[d] += random.uniform(0.01, 0.03)

            if positions[d] > 1:
                positions[d] -= 1

        await ws.send_json(positions)

        await asyncio.sleep(0.2)
