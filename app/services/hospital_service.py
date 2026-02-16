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
# Primary Geocoding Function
# -----------------------------
async def geocode_address(address: str) -> dict:
    """Geocode address using Nominatim for accurate coordinates"""
    # Try Nominatim first for most accurate results
    try:
        return await geocode_address_nominatim(address)
    except Exception as e:
        # If Nominatim fails, try Gemini as fallback
        try:
            return await geocode_address_with_gemini(address)
        except Exception:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not geocode address: {address}. Please provide a more specific address."
            )


# -----------------------------
# Nominatim Geocoding (Primary)
# -----------------------------
async def geocode_address_nominatim(address: str) -> dict:
    """Primary geocoding using Nominatim API for exact address matching"""
    url = "https://nominatim.openstreetmap.org/search"
    
    # Try with multiple search strategies for better results
    search_queries = [
        address,  # Original address
        f"{address}, India",  # Add country if not specified
    ]
    
    headers = {
        "User-Agent": "HospitalFinderAPI/1.0"
    }
    
    async with httpx.AsyncClient() as client:
        for query in search_queries:
            params = {
                "q": query,
                "format": "json",
                "limit": 5,  # Get top 5 results to find best match
                "addressdetails": 1,
                "countrycodes": "in" if "india" in query.lower() or any(city in query.lower() for city in ["hyderabad", "bangalore", "mumbai", "delhi", "chennai", "kolkata", "pune", "ahmedabad"]) else None
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if data:
                # Use the first result (most relevant)
                return {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "formatted_address": data[0].get("display_name", address)
                }
        
        # If no results found with any query
        raise HTTPException(
            status_code=404, 
            detail=f"Address not found: '{address}'. Please verify the address and try again."
        )


# -----------------------------
# Geocoding with Gemini (Fallback)
# -----------------------------
async def geocode_address_with_gemini(address: str) -> dict:
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    try:
        prompt = f"""
Given this address: "{address}"

Provide ONLY the following information in this exact format (no additional text):
Latitude: [value]
Longitude: [value]
Formatted Address: [value]

Provide precise coordinates based on the exact address given.
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
            raise HTTPException(status_code=404, detail="Could not extract coordinates")

        return {"lat": lat, "lon": lon, "formatted_address": formatted}

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Geocoding failed: {str(e)}")


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
      relation["amenity"="hospital"](around:{radius_m},{lat},{lon});
    );
    out center;
    """

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url, 
            data={"data": query},
            headers={"User-Agent": "HospitalFinderAPI/1.0"},
            timeout=30.0
        )
        resp.raise_for_status()
        return resp.json()


# -----------------------------
# Distance Calculation
# -----------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Earth's radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))


# -----------------------------
# Maps Link
# -----------------------------
def create_google_maps_link(lat1, lon1, lat2, lon2):
    return f"https://www.google.com/maps/dir/?api=1&origin={lat1},{lon1}&destination={lat2},{lon2}&travelmode=driving"