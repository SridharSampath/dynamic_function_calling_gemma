import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city: str) -> str:
    """Fetch current weather information for a city."""
    print("Fetch current weather information from get_weather")
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        city_name = data.get("name")
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return (
            f"⛅ Weather in {city_name}:\n"
            f"Temperature: {temp}°C\n"
            f"Condition: {description.capitalize()}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s"
        )

    except Exception as e:
        return f"Weather Fetch Error: {str(e)}"