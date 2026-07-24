from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models.models import Rider, Race, Result
from ..core.engine import process_race, calculate_composite_rating
from ..db import get_db

router = APIRouter()

class LeaderboardResponse(BaseModel):
    selected_disciplines: List[str]
    total_riders: int
    leaderboard: list

class RaceUploadResult(BaseModel):
    rider_id: str
    rider_name: str
    time_sec: float
    status: str = "FIN"
    is_kids: bool = False

class RaceUploadRequest(BaseModel):
    date: str
    category: str
    k_factor: float = 1.0
    results: List[RaceUploadResult]


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    disciplines: str = Query("all", description="comma-separated list of disciplines"),
    age_group: str = Query("all", description="Age group: all, adults, kids"),
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if disciplines == "all":
        selected_disciplines = ["road", "gravel", "mtb"]
    else:
        selected_disciplines = [d.strip() for d in disciplines.split(",")]

    query = db.query(Rider)

    if age_group == "adults":
        query = query.filter(Rider.is_kids == False)
    elif age_group == "kids":
        query = query.filter(Rider.is_kids == True)

    if search:
        query = query.filter(Rider.name.ilike(f"%{search}%"))

    riders = query.all()

    leaderboard_data = []

    for rider in riders:
        composite_rating = calculate_composite_rating(rider, selected_disciplines)
        if composite_rating is None:
            continue # Skip if no races in selected disciplines

        total_races = 0
        if "road" in selected_disciplines:
            total_races += rider.races_road
        if "gravel" in selected_disciplines:
            total_races += rider.races_gravel
        if "mtb" in selected_disciplines:
            total_races += rider.races_mtb

        leaderboard_data.append({
            "rider_id": rider.id,
            "name": rider.name,
            "composite_rating": composite_rating,
            "breakdown": {
                "road": rider.rating_road if rider.races_road > 0 else None,
                "gravel": rider.rating_gravel if rider.races_gravel > 0 else None,
                "mtb": rider.rating_mtb if rider.races_mtb > 0 else None
            },
            "total_races": total_races,
            "trend": rider.last_trend
        })

    # Sort by rating descending
    leaderboard_data.sort(key=lambda x: x["composite_rating"], reverse=True)

    # Apply limit
    leaderboard_data = leaderboard_data[:limit]

    # Add rank
    for idx, row in enumerate(leaderboard_data):
        row["rank"] = idx + 1

    return {
        "selected_disciplines": selected_disciplines,
        "total_riders": len(leaderboard_data),
        "leaderboard": leaderboard_data
    }


@router.post("/races")
def upload_race(race_data: RaceUploadRequest, db: Session = Depends(get_db)):
    from datetime import datetime

    # Create Race
    new_race = Race(
        date=datetime.strptime(race_data.date, "%Y-%m-%d").date(),
        category=race_data.category,
        k_factor=race_data.k_factor
    )
    db.add(new_race)
    db.flush() # To get new_race.id

    for res in race_data.results:
        # Check if rider exists, if not create
        rider = db.query(Rider).filter(Rider.id == res.rider_id).first()
        if not rider:
            rider = Rider(id=res.rider_id, name=res.rider_name, is_kids=res.is_kids)
            db.add(rider)
            db.flush()

        new_result = Result(
            race_id=new_race.id,
            rider_id=rider.id,
            time_sec=res.time_sec,
            status=res.status
        )
        db.add(new_result)

    db.commit()

    # Process race to update ratings
    process_race(db, new_race.id)

    return {"status": "success", "race_id": new_race.id}

@router.get("/riders/{rider_id}")
def get_rider_details(rider_id: str, db: Session = Depends(get_db)):
    rider = db.query(Rider).filter(Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    results = db.query(Result).filter(Result.rider_id == rider_id).all()

    history = []
    for res in results:
        if res.race:
            history.append({
                "race_id": res.race.id,
                "date": res.race.date.isoformat(),
                "category": res.race.category,
                "place": res.place,
                "time_sec": res.time_sec,
                "delta": res.delta,
                "status": res.status
            })

    # Sort history newest first
    history.sort(key=lambda x: x["date"], reverse=True)

    return {
        "rider_id": rider.id,
        "name": rider.name,
        "ratings": {
            "road": rider.rating_road,
            "gravel": rider.rating_gravel,
            "mtb": rider.rating_mtb
        },
        "history": history
    }
