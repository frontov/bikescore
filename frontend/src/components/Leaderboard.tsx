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
    <div className="w-full bg-gray-800/80 backdrop-blur-sm rounded-xl border border-gray-700/50 shadow-xl overflow-hidden">
      <div className="p-4 md:p-6 border-b border-gray-700/50 bg-gray-900/20">
        <div className="relative max-w-md">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-500" />
          </div>
          <input
            type="text"
            className="block w-full pl-11 pr-4 py-3 border border-gray-600/50 rounded-lg leading-5 bg-gray-800/50 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 sm:text-sm transition-all"
            placeholder="Поиск по имени спортсмена..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="overflow-x-auto min-h-[400px]">
        <table className="w-full text-left border-collapse">
          <thead className="bg-gray-900/50 text-xs uppercase font-bold text-gray-400 tracking-wider">
            <tr>
              <th className="px-6 py-4 rounded-tl-lg">#</th>
              <th className="px-6 py-4">Спортсмен</th>
              <th className="px-6 py-4">Рейтинг</th>
              <th className="px-6 py-4 hidden md:table-cell">Детализация</th>
              <th className="px-6 py-4 hidden sm:table-cell">Гонок</th>
              <th className="px-6 py-4 rounded-tr-lg">Тренд</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/30">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                  <div className="flex items-center justify-center gap-3">
                    <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    Обновление данных...
                  </div>
                </td>
              </tr>
            ) : riders.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500 font-medium">Ничего не найдено.</td>
              </tr>
            ) : (
              riders.map((rider) => (
                <tr
                  key={rider.rider_id}
                  className="hover:bg-blue-900/20 cursor-pointer transition-colors group"
                  onClick={() => setSelectedRider(rider)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400 font-mono group-hover:text-blue-400">{rider.rank}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm md:text-base font-semibold text-gray-100 group-hover:text-white">{rider.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-base md:text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">{rider.composite_rating.toFixed(1)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-400 space-x-2 hidden md:table-cell">
                    {rider.breakdown.road && <span className="bg-gray-800/80 border border-gray-700 px-2 py-1 rounded shadow-sm">Road: {rider.breakdown.road.toFixed(0)}</span>}
                    {rider.breakdown.gravel && <span className="bg-gray-800/80 border border-gray-700 px-2 py-1 rounded shadow-sm">Gravel: {rider.breakdown.gravel.toFixed(0)}</span>}
                    {rider.breakdown.mtb && <span className="bg-gray-800/80 border border-gray-700 px-2 py-1 rounded shadow-sm">MTB: {rider.breakdown.mtb.toFixed(0)}</span>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400 hidden sm:table-cell">{rider.total_races}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{renderTrend(rider.trend)}</td>
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
