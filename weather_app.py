from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Open-Meteo APIs
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"


@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")

    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    # Step 1: Get latitude & longitude from Geocoding API
    geo_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    geo_response = requests.get(GEOCODING_API, params=geo_params)

    if geo_response.status_code != 200 or "results" not in geo_response.json():
        return jsonify({"error": "Unable to fetch location data"}), 500

    geo_data = geo_response.json()["results"][0]
    latitude = geo_data["latitude"]
    longitude = geo_data["longitude"]
    country = geo_data["country"]

    # Step 2: Fetch weather data
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    }

    weather_response = requests.get(WEATHER_API, params=weather_params)

    if weather_response.status_code != 200:
        return jsonify({"error": "Unable to fetch weather data"}), 500

    weather_data = weather_response.json()["current_weather"]

    # Step 3: JSON Response
    return jsonify({
        "city": city,
        "country": country,
        "latitude": latitude,
        "longitude": longitude,
        "temperature_celsius": weather_data["temperature"],
        "windspeed_kmh": weather_data["windspeed"],
        "weather_code": weather_data["weathercode"],
        "time": weather_data["time"]
    })


if __name__ == "__main__":
    app.run(debug=True)
