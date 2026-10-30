import requests
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

app = FastAPI()

load_dotenv()

TOMTOM_API_KEY = os.getenv("TOMTOM_KEY")


@app.get("/api/travel-time")
def predict_travel_time(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float
):
    if not TOMTOM_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="TomTom API key is not configured"
        )

    locations = (
        f"{origin_lat},{origin_lon}:"
        f"{destination_lat},{destination_lon}"
    )

    url = (
        f"https://api.tomtom.com/routing/1/"
        f"calculateRoute/{locations}/json"
    )

    params = {
        "key": TOMTOM_API_KEY,
        "traffic": "true",
        "computeTravelTimeFor": "all"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="TomTom routing service failed"
        )

    data = response.json()
    summary = data["routes"][0]["summary"]

    return {
    "distance_km": round(
        summary["lengthInMeters"] / 1000, 2
    ),
    "traffic_eta_minutes": round(
        summary["travelTimeInSeconds"] / 60, 2
    ),
    "free_flow_eta_minutes": round(
        summary["noTrafficTravelTimeInSeconds"] / 60, 2
    ),
    "historic_traffic_eta_minutes": round(
        summary["historicTrafficTravelTimeInSeconds"] / 60, 2
    ),
    "traffic_delay_minutes": round(
        summary["trafficDelayInSeconds"] / 60, 2
    ),
    "raw_summary": summary

    }