import React, { useState, useEffect } from 'react';
import { Search, ChevronUp, ChevronDown } from 'lucide-react';
import { fetchLeaderboard, type LeaderboardRider } from '../services/apiClient';
import RiderCard from './RiderCard';

interface LeaderboardProps {
  selectedDisciplines: string[];
  ageGroup: string;
  gender: string;
}

const Leaderboard: React.FC<LeaderboardProps> = ({ selectedDisciplines, ageGroup, gender }) => {
  const [riders, setRiders] = useState<LeaderboardRider[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedRider, setSelectedRider] = useState<LeaderboardRider | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const disciplinesStr = selectedDisciplines.length > 0 ? selectedDisciplines.join(',') : 'all';
        const data = await fetchLeaderboard(disciplinesStr, ageGroup, gender, search);
        setRiders(data.leaderboard);
      } catch (error) {
        console.error("Error fetching leaderboard", error);
      }
      setLoading(false);
    };

    const debounce = setTimeout(loadData, 300);
    return () => clearTimeout(debounce);
  }, [selectedDisciplines, ageGroup, gender, search]);

  const renderTrend = (trend: number) => {
    if (trend > 0) return <span className="text-green-500 flex items-center"><ChevronUp size={16}/> {trend.toFixed(1)}</span>;
    if (trend < 0) return <span className="text-red-500 flex items-center"><ChevronDown size={16}/> {Math.abs(trend).toFixed(1)}</span>;
    return <span className="text-gray-500">-</span>;
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-gray-800 rounded-lg shadow-xl overflow-hidden">
      <div className="p-4 border-b border-gray-700">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-600 rounded-md leading-5 bg-gray-700 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="Search Rider..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">#</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Rider</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Rating</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Breakdown</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Races</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Trend</th>
            </tr>
          </thead>
          <tbody className="bg-gray-800 divide-y divide-gray-700">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-400">Loading...</td>
              </tr>
            ) : riders.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-400">No riders found.</td>
              </tr>
            ) : (
              riders.map((rider) => (
                <tr
                  key={rider.rider_id}
                  className="hover:bg-gray-700 cursor-pointer transition-colors"
                  onClick={() => setSelectedRider(rider)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 font-mono">{rider.rank}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{rider.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-400">{rider.composite_rating.toFixed(1)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-400 space-x-2">
                    {rider.breakdown.road && <span className="bg-gray-900 px-2 py-1 rounded">Rd: {rider.breakdown.road.toFixed(0)}</span>}
                    {rider.breakdown.gravel && <span className="bg-gray-900 px-2 py-1 rounded">Gr: {rider.breakdown.gravel.toFixed(0)}</span>}
                    {rider.breakdown.mtb && <span className="bg-gray-900 px-2 py-1 rounded">MTB: {rider.breakdown.mtb.toFixed(0)}</span>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{rider.total_races}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{renderTrend(rider.trend)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {selectedRider && (
        <RiderCard rider={selectedRider} onClose={() => setSelectedRider(null)} />
      )}
    </div>
  );
};

export default Leaderboard;
