from pydantic import BaseModel, Field
from typing import List, Optional

class AddressRequest(BaseModel):
    address: str = Field(..., description="Current address of the user")
    radius_km: float = Field(default=5.0, ge=0.1, le=50, description="Search radius in kilometers")

class Hospital(BaseModel):
    name: str
    address: Optional[str] = None
    distance_km: float
    latitude: float
    longitude: float
    google_maps_link: str
    phone: Optional[str] = None
    emergency: Optional[str] = None

class HospitalResponse(BaseModel):
    origin_address: str
    origin_coordinates: dict
    total_hospitals_found: int
    hospitals: List[Hospital]
