from pydantic import BaseModel, Field
from typing import List, Optional

class Result(BaseModel):
    rider_id: str = Field(..., description="Unique identifier for the rider")
    rider_name: str = Field(..., description="Full name of the rider")
    time_sec: int = Field(..., description="Finish time in seconds")
    status: str = Field(..., description="Finish status (e.g., FIN, DNF, DSQ)")
    is_kids: Optional[bool] = Field(None, description="Flag indicating if the rider participated in a kids race")

class RacePayload(BaseModel):
    date: str = Field(..., description="Date of the race in YYYY-MM-DD format")
    category: str = Field(..., description="Category of the race (e.g., road, gravel, mtb)")
    k_factor: float = Field(1.0, description="Difficulty factor of the race")
    results: List[Result] = Field(..., description="List of results for the race")
