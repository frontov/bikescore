import { useState } from 'react';
import DisciplineSelector from './components/DisciplineSelector';
import Leaderboard from './components/Leaderboard';

function App() {
  const [selectedDisciplines, setSelectedDisciplines] = useState<string[]>(['road', 'gravel', 'mtb']);

  return (
    <div className="min-h-screen bg-[#242424] text-white p-8 font-sans">
      <div className="max-w-4xl mx-auto mb-8">
        <h1 className="text-4xl font-bold mb-2">VeloRank</h1>
        <p className="text-gray-400">Dynamic Cycling Rating System (Pairwise Anchor Model)</p>
      </div>

      <DisciplineSelector
        selectedDisciplines={selectedDisciplines}
        onChange={setSelectedDisciplines}
      />

      <Leaderboard selectedDisciplines={selectedDisciplines} />
    </div>
  );
}

export default App;
