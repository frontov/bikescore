import { useState } from 'react';
import DisciplineSelector from './components/DisciplineSelector';
import Leaderboard from './components/Leaderboard';

function App() {
  const [selectedDisciplines, setSelectedDisciplines] = useState<string[]>(['road', 'gravel', 'mtb']);
  const [ageGroup, setAgeGroup] = useState<string>('adults');
  const [gender, setGender] = useState<string>('M');

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-white p-4 md:p-8 font-sans">
      <div className="max-w-[1400px] mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-2 bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">VeloRank</h1>
          <p className="text-gray-400 text-sm md:text-base">Dynamic Cycling Rating System (Pairwise Anchor Model)</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Controls Container */}
          <div className="flex flex-col sm:flex-row lg:flex-col xl:flex-row gap-4 p-5 bg-gray-800/80 backdrop-blur-sm rounded-xl border border-gray-700/50 shadow-xl">
            <div className="flex flex-col gap-3 w-full">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Возраст</span>
              <div className="flex flex-wrap gap-2">
                {['adults', 'kids'].map((group) => (
                  <button
                    key={group}
                    onClick={() => setAgeGroup(group)}
                    className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                      ageGroup === group
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                        : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600 hover:text-white'
                    }`}
                  >
                    {group === 'adults' ? 'Взрослые' : 'Дети'}
                  </button>
                ))}
              </div>
            </div>

            <div className="w-full sm:w-px lg:w-full xl:w-px bg-gray-700/50 my-2 sm:my-0 lg:my-2 xl:my-0" />

            <div className="flex flex-col gap-3 w-full">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Пол</span>
              <div className="flex flex-wrap gap-2">
                {['M', 'F'].map((g) => (
                  <button
                    key={g}
                    onClick={() => setGender(g)}
                    className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                      gender === g
                        ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                        : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600 hover:text-white'
                    }`}
                  >
                    {g === 'M' ? 'Мужчины' : 'Женщины'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex">
            <DisciplineSelector
              selectedDisciplines={selectedDisciplines}
              onChange={setSelectedDisciplines}
            />
          </div>
        </div>

        <Leaderboard selectedDisciplines={selectedDisciplines} ageGroup={ageGroup} gender={gender} />
      </div>
    </div>
  );
}

export default App;
