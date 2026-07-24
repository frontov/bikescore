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
    <div className="flex gap-4 p-4 bg-gray-800 rounded-lg shadow-md mb-6 w-full max-w-4xl mx-auto items-center">
      <span className="font-semibold text-gray-200">Filters:</span>
      <div className="flex gap-2">
        {disciplines.map(({ id, label }) => {
          const isSelected = selectedDisciplines.includes(id);
          return (
            <button
              key={id}
              onClick={() => toggleDiscipline(id)}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                isSelected
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
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
