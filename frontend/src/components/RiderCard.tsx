import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { X } from 'lucide-react';
import { type LeaderboardRider } from '../services/apiClient';

interface RiderCardProps {
  rider: LeaderboardRider;
  onClose: () => void;
}

const RiderCard: React.FC<RiderCardProps> = ({ rider, onClose }) => {
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

        <div className="p-6">
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
        </div>
      </div>
    </div>
  );
};

export default RiderCard;
