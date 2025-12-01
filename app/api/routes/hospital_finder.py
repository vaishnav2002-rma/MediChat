from fastapi import APIRouter, HTTPException
from app.models.hospital_models import AddressRequest, HospitalResponse, Hospital
from app.services.hospital_service import (
    geocode_address_with_gemini,
    find_nearby_hospitals,
    calculate_distance,
    create_google_maps_link
)

router = APIRouter(prefix="/hospital", tags=["Hospital Finder"])


@router.post("/find", response_model=HospitalResponse)
async def find_hospitals(request: AddressRequest):
    try:
        # Step 1: Geocode
        location = await geocode_address_with_gemini(request.address)
        lat = location["lat"]
        lon = location["lon"]

        # Step 2: Query Overpass
        overpass = await find_nearby_hospitals(lat, lon, request.radius_km)

        hospitals = []
        for item in overpass.get("elements", []):
            if item["type"] == "node":
                hlat = item["lat"]
                hlon = item["lon"]
            elif "center" in item:
                hlat = item["center"]["lat"]
                hlon = item["center"]["lon"]
            else:
                continue

            distance = calculate_distance(lat, lon, hlat, hlon)
            if distance > request.radius_km:
                continue

            tags = item.get("tags", {})
            name = tags.get("name", "Unnamed Hospital")

            address_parts = [tags.get(k) for k in ["addr:street", "addr:city", "addr:state"] if tags.get(k)]
            address = ", ".join(address_parts) if address_parts else None

            hospitals.append(
                Hospital(
                    name=name,
                    address=address,
                    distance_km=round(distance, 2),
                    latitude=hlat,
                    longitude=hlon,
                    google_maps_link=create_google_maps_link(lat, lon, hlat, hlon),
                    phone=tags.get("phone"),
                    emergency=tags.get("emergency")
                )
            )

        # Sort by nearest
        hospitals.sort(key=lambda h: h.distance_km)

        return HospitalResponse(
            origin_address=location["formatted_address"],
            origin_coordinates={"latitude": lat, "longitude": lon},
            total_hospitals_found=len(hospitals),
            hospitals=hospitals
        )

    except Exception as e:
        raise HTTPException(500, f"Internal error: {e}")
