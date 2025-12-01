import httpx
import os
from urllib.parse import quote
from fastapi import HTTPException
from google.genai import Client
from app.models.hospital_models import Hospital
from dotenv import load_dotenv

load_dotenv()

# Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


# -----------------------------
# Geocoding with Gemini
# -----------------------------
async def geocode_address_with_gemini(address: str) -> dict:
    if not gemini_client:
        return await geocode_address_nominatim(address)

    try:
        prompt = f"""
Given this address: "{address}"

Provide:
Latitude: [value]
Longitude: [value]
Formatted Address: [value]
"""

        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )

        text = response.text.strip()
        lat = lon = None
        formatted = address

        for line in text.split("\n"):
            if line.startswith("Latitude:"):
                lat = float(line.split(":")[1].strip())
            elif line.startswith("Longitude:"):
                lon = float(line.split(":")[1].strip())
            elif line.startswith("Formatted Address:"):
                formatted = line.split(":", 1)[1].strip()

        if lat is None or lon is None:
            return await geocode_address_nominatim(address)

        return {"lat": lat, "lon": lon, "formatted_address": formatted}

    except Exception:
        return await geocode_address_nominatim(address)


# -----------------------------
# Nominatim Fallback
# -----------------------------
async def geocode_address_nominatim(address: str) -> dict:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={"User-Agent": "HospitalFinder"})
        resp.raise_for_status()
        data = resp.json()

        if not data:
            raise HTTPException(404, "Address not found")

        return {
            "lat": float(data[0]["lat"]),
            "lon": float(data[0]["lon"]),
            "formatted_address": data[0].get("display_name", address)
        }


# -----------------------------
# Overpass Hospital Search
# -----------------------------
async def find_nearby_hospitals(lat: float, lon: float, radius_km: float):
    url = "https://overpass-api.de/api/interpreter"
    radius_m = radius_km * 1000

    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      way["amenity"="hospital"](around:{radius_m},{lat},{lon});
    );
    out center;
    """

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data={"data": query})
        resp.raise_for_status()
        return resp.json()


# -----------------------------
# Distance Calculation
# -----------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))


# -----------------------------
# Maps Link
# -----------------------------
def create_google_maps_link(lat1, lon1, lat2, lon2):
    return f"https://www.google.com/maps/dir/?api=1&origin={lat1},{lon1}&destination={lat2},{lon2}&travelmode=driving"
