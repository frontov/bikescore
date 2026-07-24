import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface Breakdown {
  road: number | null;
  gravel: number | null;
  mtb: number | null;
}

export interface LeaderboardRider {
  rank: number;
  rider_id: string;
  name: string;
  composite_rating: number;
  breakdown: Breakdown;
  total_races: number;
  trend: number;
}

export interface RaceHistory {
  race_id: number;
  date: string;
  category: string;
  place: number | null;
  time_sec: number;
  delta: number | null;
  status: string;
}

export interface RiderDetails {
  rider_id: string;
  name: string;
  ratings: {
    road: number;
    gravel: number;
    mtb: number;
  };
  history: RaceHistory[];
}

export interface LeaderboardResponse {
  selected_disciplines: string[];
  total_riders: number;
  leaderboard: LeaderboardRider[];
}

export const fetchLeaderboard = async (
  disciplines: string,
  ageGroup: string,
  gender: string,
  search?: string
): Promise<LeaderboardResponse> => {
  const params: Record<string, string> = { disciplines, age_group: ageGroup, gender };
  if (search) {
    params.search = search;
  }

  const response = await axios.get(`${API_BASE_URL}/leaderboard`, { params });
  return response.data;
};

export const fetchRiderDetails = async (riderId: string): Promise<RiderDetails> => {
  const response = await axios.get(`${API_BASE_URL}/riders/${riderId}`);
  return response.data;
};
