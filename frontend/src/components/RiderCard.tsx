import React, { useEffect, useState } from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { X, Trophy, Timer, TrendingUp, TrendingDown } from 'lucide-react';
import { type LeaderboardRider, fetchRiderDetails, type RiderDetails } from '../services/apiClient';

interface RiderCardProps {
  rider: LeaderboardRider;
  onClose: () => void;
}

const RiderCard: React.FC<RiderCardProps> = ({ rider, onClose }) => {
  const [details, setDetails] = useState<RiderDetails | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDetails = async () => {
      setLoading(true);
      try {
        const data = await fetchRiderDetails(rider.rider_id);
        setDetails(data);
      } catch (error) {
        console.error("Failed to load rider details", error);
      }
      setLoading(false);
    };
    loadDetails();
  }, [rider.rider_id]);

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const chartData = [
    { subject: 'Road', A: rider.breakdown.road || 0, fullMark: 2500 },
    { subject: 'Gravel', A: rider.breakdown.gravel || 0, fullMark: 2500 },
    { subject: 'MTB', A: rider.breakdown.mtb || 0, fullMark: 2500 },
  ];

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-800 text-gray-100 rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b border-gray-700">
          <div>
            <h2 className="text-2xl font-bold">{rider.name}</h2>
            <p className="text-gray-400">Composite Rating: {rider.composite_rating.toFixed(1)}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-700 rounded-full transition-colors">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 space-y-8">
          <div className="grid md:grid-cols-2 gap-8">
            <div className="h-64 bg-gray-900 rounded-lg p-4">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
                  <PolarGrid stroke="#4B5563" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#9CA3AF' }} />
                  <PolarRadiusAxis angle={30} domain={[0, 'dataMax + 500']} stroke="#4B5563" tick={{ fill: '#9CA3AF' }} />
                  <Radar
                    name="Rating"
                    dataKey="A"
                    stroke="#3B82F6"
                    fill="#3B82F6"
                    fillOpacity={0.5}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold border-b border-gray-700 pb-2">Stats Breakdown</h3>
              <div className="space-y-2">
                <div className="flex justify-between p-2 bg-gray-700 rounded">
                  <span>Road Rating</span>
                  <span className="font-mono">{rider.breakdown.road ? rider.breakdown.road.toFixed(1) : 'N/A'}</span>
                </div>
                <div className="flex justify-between p-2 bg-gray-700 rounded">
                  <span>Gravel Rating</span>
                  <span className="font-mono">{rider.breakdown.gravel ? rider.breakdown.gravel.toFixed(1) : 'N/A'}</span>
                </div>
                <div className="flex justify-between p-2 bg-gray-700 rounded">
                  <span>MTB Rating</span>
                  <span className="font-mono">{rider.breakdown.mtb ? rider.breakdown.mtb.toFixed(1) : 'N/A'}</span>
                </div>
                <div className="flex justify-between p-2 bg-gray-700 rounded mt-4">
                  <span>Total Races</span>
                  <span className="font-mono">{rider.total_races}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-900 rounded-lg overflow-hidden">
            <h3 className="text-lg font-semibold p-4 bg-gray-800 border-b border-gray-700">Race History</h3>
            {loading ? (
              <div className="p-8 text-center text-gray-400">Loading history...</div>
            ) : !details?.history.length ? (
              <div className="p-8 text-center text-gray-400">No race history found.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-gray-400 uppercase bg-gray-800/50">
                    <tr>
                      <th className="px-4 py-3">Date</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Place</th>
                      <th className="px-4 py-3">Time</th>
                      <th className="px-4 py-3">Delta</th>
                    </tr>
                  </thead>
                  <tbody>
                    {details.history.map((race, idx) => (
                      <tr key={idx} className="border-b border-gray-800 hover:bg-gray-800/50">
                        <td className="px-4 py-3 font-mono text-gray-300">{race.date}</td>
                        <td className="px-4 py-3">
                          <span className="bg-gray-700 px-2 py-1 rounded text-xs uppercase tracking-wider">{race.category}</span>
                        </td>
                        <td className="px-4 py-3">
                          {race.place ? (
                            <span className="flex items-center gap-1 font-bold text-white">
                              {race.place <= 3 && <Trophy size={14} className={race.place === 1 ? "text-yellow-400" : race.place === 2 ? "text-gray-300" : "text-amber-600"} />}
                              {race.place}
                            </span>
                          ) : (
                            <span className="text-gray-500">{race.status}</span>
                          )}
                        </td>
                        <td className="px-4 py-3 font-mono text-gray-300 flex items-center gap-1">
                          <Timer size={14} className="text-gray-500" />
                          {formatTime(race.time_sec)}
                        </td>
                        <td className="px-4 py-3">
                          {race.delta !== null && race.delta !== 0 ? (
                            <span className={`flex items-center gap-1 font-mono ${race.delta > 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {race.delta > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                              {Math.abs(race.delta).toFixed(1)}
                            </span>
                          ) : (
                            <span className="text-gray-500">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiderCard;
