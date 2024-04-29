import requests
from src.database import SessionLocal
import src.models as models
from fastapi import APIRouter, HTTPException, status

from src.locations.schemas import Location, LocationsWithWeatherCondition

router = APIRouter()


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


@router.get("/", response_model=list[LocationsWithWeatherCondition], status_code=200)
def get_all_locations():
    locations = db.query(models.Location).all()
    locationsWithWeatherCondition = []
    for location in locations:
        current_weather_condition = fetch_current(location.latitude, location.longitude)
        locationsWithWeatherCondition.append(LocationsWithWeatherCondition(
            name=location.name,
            latitude=location.latitude,
            longitude=location.longitude,
            current_weather_condition=current_weather_condition,
        ))

    return locationsWithWeatherCondition


@router.post("/", response_model=Location, status_code=status.HTTP_201_CREATED)
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


@router.delete("/{id}")
def delete_item(id: int):
    location_to_delete = db.query(models.Location).filter(models.Location.id == id).first()

    if location_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location Not Found")

    db.delete(location_to_delete)
    db.commit()

    return location_to_delete