import models
import requests
from database import SessionLocal
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class Location(BaseModel):  # serializer
    name: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True


class Response(Location):
    current_weather_condition: object


db = SessionLocal()


def fetch_current(latitude, longitude):
    api_url = (
        "https://api.open-meteo.com/v1/forecast?latitude="
        + str(latitude)
        + "&longitude="
        + str(longitude)
        + "&current=temperature_2m,rain"
    )
    weather_data = requests.get(api_url).json()

    return weather_data


def fetch_forecast(latitude, longitude):
    api_url = (
        "https://api.open-meteo.com/v1/forecast?latitude="
        + str(latitude)
        + "&longitude="
        + str(longitude)
        + "&forecast_days="
        + str(7)
        + "&daily=temperature_2m_max,temperature_2m_min"
    )
    weather_data = requests.get(api_url).json()

    return weather_data


@app.get("/locations", response_model=list[Response], status_code=200)
def get_all_locations():
    locations = db.query(models.Location).all()
    responses = []
    for location in locations:
        current_weather_condition = fetch_current(location.latitude, location.longitude)
        response = Response(
            name=location.name,
            latitude=location.latitude,
            longitude=location.longitude,
            current_weather_condition=current_weather_condition,
        )
        responses.append(response)

    return responses


@app.post("/locations", response_model=Location, status_code=status.HTTP_201_CREATED)
def create_an_location(location: Location):
    db_location = db.query(models.Location).filter(models.Location.name == location.name).first()

    if db_location is not None:
        raise HTTPException(status_code=400, detail="Location already exists")

    new_location = models.Location(
        name=location.name,
        latitude=location.latitude,
        longitude=location.longitude,
    )

    db.add(new_location)
    db.commit()

    return new_location


@app.delete("/locations/{id}")
def delete_item(id: int):
    location_to_delete = db.query(models.Location).filter(models.Location.id == id).first()

    if location_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location Not Found")

    db.delete(location_to_delete)
    db.commit()

    return location_to_delete


@app.get("/forecast/{location_id}", response_model=object, status_code=200)
def get_forecast(location_id):
    location = db.query(models.Location).filter(models.Location.id == location_id).first()
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location Not Found")

    response = fetch_forecast(location.latitude, location.longitude)

    return response
