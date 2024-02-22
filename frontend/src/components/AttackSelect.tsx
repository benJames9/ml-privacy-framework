"use client";
import React, { useState } from 'react';

interface AttackSelectProps {
  attacks: string[];
  onChange: (model: string) => void;
}

const AttackSelect: React.FC<AttackSelectProps> = ({
  attacks,
  onChange,
}) => {
  const [internalSelectedAttack, setInternalSelectedAttack] = useState(attacks[0]);
  const handleAttackSelect = (attack: string) => {
    setInternalSelectedAttack(attack);
    onChange(attack);
    const modelSelect = document.getElementById("model-select-header");
    modelSelect!.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="grid grid-cols-2 gap-8">
      {attacks.map((attack) => (
        <button
          key={attack}
          type="button"
          className={
            `bg-gray-900 whitespace-pre text-white hover:bg-gray-600 border border-gray-300 text-gray-700 ${internalSelectedAttack === attack ? "ring-4 ring-blue-500" : ""} font-medium rounded-lg text-center inline-flex items-center px-5 py-4 text-base w-full justify-center w-48 h-32 min-w-32 text-xl`
          }
          onClick={() => handleAttackSelect(attack)}
        >
          <span>{attack}</span>
        </button>
      ))}
    </div>
  );
};

export default AttackSelect;
