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
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-2 md:p-6 z-50 overflow-hidden">
      <div className="bg-gray-800 border border-gray-700/50 text-gray-100 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[95vh] flex flex-col">
        <div className="flex justify-between items-center p-5 md:p-6 border-b border-gray-700/50 bg-gray-900/30 shrink-0">
          <div>
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight">{rider.name}</h2>
            <p className="text-blue-400 font-medium mt-1">Рейтинг: {rider.composite_rating.toFixed(1)}</p>
          </div>
          <button onClick={onClose} className="p-2 bg-gray-800 hover:bg-gray-700 rounded-full transition-colors self-start border border-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="p-5 md:p-8 space-y-8 overflow-y-auto custom-scrollbar">
          <div className="grid md:grid-cols-2 gap-6 md:gap-8">
            <div className="h-64 md:h-80 bg-gray-900/50 rounded-xl p-2 md:p-4 border border-gray-800">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 'dataMax + 500']} stroke="#374151" tick={{ fill: '#6B7280', fontSize: 10 }} />
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

            <div className="space-y-5 flex flex-col justify-center">
              <h3 className="text-xl font-bold border-b border-gray-700/50 pb-3 text-gray-200">Детализация рейтинга</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3.5 bg-gray-800/80 rounded-xl border border-gray-700/50">
                  <span className="font-medium text-gray-300">Шоссе (Road)</span>
                  <span className="font-mono text-lg text-blue-400 font-bold">{rider.breakdown.road ? rider.breakdown.road.toFixed(1) : 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center p-3.5 bg-gray-800/80 rounded-xl border border-gray-700/50">
                  <span className="font-medium text-gray-300">Грэвел (Gravel)</span>
                  <span className="font-mono text-lg text-amber-500 font-bold">{rider.breakdown.gravel ? rider.breakdown.gravel.toFixed(1) : 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center p-3.5 bg-gray-800/80 rounded-xl border border-gray-700/50">
                  <span className="font-medium text-gray-300">МТБ (MTB)</span>
                  <span className="font-mono text-lg text-emerald-500 font-bold">{rider.breakdown.mtb ? rider.breakdown.mtb.toFixed(1) : 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center p-3.5 bg-gray-900/80 rounded-xl border border-gray-700 mt-6 shadow-inner">
                  <span className="font-bold text-gray-300 uppercase text-xs tracking-wider">Всего гонок учтено</span>
                  <span className="font-mono text-xl font-bold">{rider.total_races}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-900/50 rounded-xl overflow-hidden border border-gray-700/50 shadow-inner">
            <h3 className="text-lg font-bold p-5 bg-gray-800/80 border-b border-gray-700/50">История заездов</h3>
            {loading ? (
              <div className="p-12 text-center text-gray-500 flex flex-col items-center gap-3">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                Загрузка истории...
              </div>
            ) : !details?.history.length ? (
              <div className="p-12 text-center text-gray-500 font-medium">История гонок пуста.</div>
            ) : (
              <div className="overflow-x-auto custom-scrollbar pb-2">
                <table className="w-full text-left border-collapse whitespace-nowrap">
                  <thead className="text-xs text-gray-400 uppercase bg-gray-900/80 font-bold tracking-wider">
                    <tr>
                      <th className="px-5 py-4">Дата</th>
                      <th className="px-5 py-4">Дисциплина</th>
                      <th className="px-5 py-4 text-center">Место</th>
                      <th className="px-5 py-4 text-right">Время</th>
                      <th className="px-5 py-4 text-right">Очки</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/80">
                    {details.history.map((race, idx) => (
                      <tr key={idx} className="hover:bg-gray-800/50 transition-colors">
                        <td className="px-5 py-4 font-mono text-sm text-gray-300">{race.date}</td>
                        <td className="px-5 py-4">
                          <span className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider ${
                            race.category === 'mtb' ? 'bg-emerald-900/50 text-emerald-400 border border-emerald-800/50' :
                            race.category === 'gravel' ? 'bg-amber-900/50 text-amber-400 border border-amber-800/50' :
                            'bg-blue-900/50 text-blue-400 border border-blue-800/50'
                          }`}>
                            {race.category}
                          </span>
                        </td>
                        <td className="px-5 py-4 text-center">
                          {race.place ? (
                            <span className="inline-flex items-center justify-center gap-1.5 font-bold text-base w-full">
                              {race.place <= 3 && <Trophy size={16} className={race.place === 1 ? "text-yellow-400" : race.place === 2 ? "text-gray-300" : "text-amber-600"} />}
                              <span className={race.place <= 3 ? "text-white" : "text-gray-400"}>{race.place}</span>
                            </span>
                          ) : (
                            <span className="text-gray-500 font-medium">{race.status}</span>
                          )}
                        </td>
                        <td className="px-5 py-4 font-mono text-sm text-gray-300 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Timer size={14} className="text-gray-500" />
                            {formatTime(race.time_sec)}
                          </div>
                        </td>
                        <td className="px-5 py-4 text-right">
                          {race.delta !== null && race.delta !== 0 ? (
                            <span className={`inline-flex items-center gap-1.5 font-mono font-bold ${race.delta > 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {race.delta > 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                              {race.delta > 0 ? '+' : ''}{race.delta.toFixed(1)}
                            </span>
                          ) : (
                            <span className="text-gray-600 font-mono">0.0</span>
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
