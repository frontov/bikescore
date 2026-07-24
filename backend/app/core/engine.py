from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from ..models.models import Rider, Race, Result

def process_race(session: Session, race_id: int):
    race = session.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise ValueError("Race not found")

    results = session.query(Result).filter(Result.race_id == race_id).all()

    # Filter DNF/DSQ
    valid_results = [r for r in results if r.status not in ("DNF", "DSQ") and r.time_sec is not None and r.time_sec > 0]

    if not valid_results:
        return

    # Sort valid_results by time to assign places
    valid_results.sort(key=lambda r: r.time_sec)

    # Assign places
    for idx, r in enumerate(valid_results):
        r.place = idx + 1

    # Find winner time
    winner_time = valid_results[0].time_sec

    # Filter outliers (>30% of winner time)
    # i.e., time_sec <= winner_time * 1.3
    filtered_results = [r for r in valid_results if r.time_sec <= winner_time * 1.3]

    N = len(filtered_results)
    if N < 2:
        # No one to compare with
        return

    k_factor = race.k_factor
    category = race.category # 'road', 'gravel', 'mtb'

    # Get old ratings and rider objects
    rider_data = {}
    for res in filtered_results:
        rider = res.rider
        # Initialize delta to 0 in case they get skipped but we still need the record
        res.delta = 0.0
        if category == 'road':
            old_rating = rider.rating_road
        elif category == 'gravel':
            old_rating = rider.rating_gravel
        else: # mtb
            old_rating = rider.rating_mtb

        rider_data[res.rider_id] = {
            'rider': rider,
            'time': res.time_sec,
            'old_rating': old_rating
        }

    deltas = {}

    for rider_id_A, data_A in rider_data.items():
        delta_sum = 0
        for rider_id_B, data_B in rider_data.items():
            if rider_id_A == rider_id_B:
                continue

            ratio_a_b = data_B['time'] / data_A['time']
            delta_sum += (ratio_a_b * data_B['old_rating']) - data_A['old_rating']

        delta_ra = k_factor * (1.0 / (N - 1)) * delta_sum
        deltas[rider_id_A] = delta_ra

    # Save delta back to result model
    for res in filtered_results:
        if res.rider_id in deltas:
            res.delta = deltas[res.rider_id]

    # Apply deltas and increment race counts
    for rider_id, delta in deltas.items():
        rider = rider_data[rider_id]['rider']
        rider.last_trend = delta
        if category == 'road':
            rider.rating_road += delta
            rider.races_road += 1
        elif category == 'gravel':
            rider.rating_gravel += delta
            rider.races_gravel += 1
        else: # mtb
            rider.rating_mtb += delta
            rider.races_mtb += 1

    session.commit()

def calculate_composite_rating(rider: Rider, selected_disciplines: List[str]) -> float:
    total_weighted_rating = 0.0
    total_races = 0

    if "road" in selected_disciplines:
        total_weighted_rating += rider.rating_road * rider.races_road
        total_races += rider.races_road
    if "gravel" in selected_disciplines:
        total_weighted_rating += rider.rating_gravel * rider.races_gravel
        total_races += rider.races_gravel
    if "mtb" in selected_disciplines:
        total_weighted_rating += rider.rating_mtb * rider.races_mtb
        total_races += rider.races_mtb

    if total_races == 0:
        return None

    return total_weighted_rating / total_races
