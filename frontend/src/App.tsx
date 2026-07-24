import { useState } from 'react';
import DisciplineSelector from './components/DisciplineSelector';
import Leaderboard from './components/Leaderboard';

function App() {
  const [selectedDisciplines, setSelectedDisciplines] = useState<string[]>(['road', 'gravel', 'mtb']);
  const [ageGroup, setAgeGroup] = useState<string>('all');

  return (
    <div className="min-h-screen bg-[#242424] text-white p-8 font-sans">
      <div className="max-w-4xl mx-auto mb-8">
        <h1 className="text-4xl font-bold mb-2">VeloRank</h1>
        <p className="text-gray-400">Dynamic Cycling Rating System (Pairwise Anchor Model)</p>
      </div>

      <div className="flex gap-4 p-4 bg-gray-800 rounded-lg shadow-md mb-6 w-full max-w-4xl mx-auto items-center">
        <span className="font-semibold text-gray-200">Category:</span>
        <div className="flex gap-2">
          {['all', 'adults', 'kids'].map((group) => (
            <button
              key={group}
              onClick={() => setAgeGroup(group)}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                ageGroup === group
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {group === 'all' ? 'Все' : group === 'adults' ? 'Взрослые' : 'Дети'}
            </button>
          ))}
        </div>
      </div>

      <DisciplineSelector
        selectedDisciplines={selectedDisciplines}
        onChange={setSelectedDisciplines}
      />

      <Leaderboard selectedDisciplines={selectedDisciplines} ageGroup={ageGroup} />
    </div>
  );
}

export default App;
