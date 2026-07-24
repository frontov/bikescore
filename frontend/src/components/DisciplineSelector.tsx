import React from 'react';

interface DisciplineSelectorProps {
  selectedDisciplines: string[];
  onChange: (disciplines: string[]) => void;
}

const DisciplineSelector: React.FC<DisciplineSelectorProps> = ({ selectedDisciplines, onChange }) => {
  const toggleDiscipline = (disc: string) => {
    if (selectedDisciplines.includes(disc)) {
      if (selectedDisciplines.length > 1) { // Prevent deselecting all
        onChange(selectedDisciplines.filter((d) => d !== disc));
      }
    } else {
      onChange([...selectedDisciplines, disc]);
    }
  };

  const disciplines = [
    { id: 'road', label: 'Road' },
    { id: 'gravel', label: 'Gravel' },
    { id: 'mtb', label: 'MTB' }
  ];

  return (
    <div className="flex flex-col gap-3 p-5 bg-gray-800/80 backdrop-blur-sm rounded-xl border border-gray-700/50 shadow-xl w-full">
      <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Дисциплины (Множественный выбор)</span>
      <div className="flex flex-wrap gap-2 h-full">
        {disciplines.map(({ id, label }) => {
          const isSelected = selectedDisciplines.includes(id);
          return (
            <button
              key={id}
              onClick={() => toggleDiscipline(id)}
              className={`flex-1 min-w-[100px] px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 border-2 ${
                isSelected
                  ? 'bg-transparent border-blue-500 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.2)]'
                  : 'bg-gray-700/30 border-transparent text-gray-400 hover:border-gray-600 hover:text-gray-200'
              }`}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default DisciplineSelector;
