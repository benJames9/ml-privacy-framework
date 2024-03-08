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
  const [internalSelectedAttack, setInternalSelectedAttack] = useState("");
  const handleAttackSelect = (attack: string) => {
    setInternalSelectedAttack(attack);
    onChange(attack);
    const modelSelect = document.getElementById("model-select-header");
    modelSelect!.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="grid grid-cols-3 gap-8">
      {attacks.map((attack) => (
        <button
          key={attack}
          type="button"
          className={
            `bg-gray-900 whitespace-pre text-white hover:bg-gray-600 border border-gray-300 ${internalSelectedAttack === attack ? "ring-4 ring-blue-500" : ""} font-medium rounded-lg center px-5 py-4 w-full w-48 h-32 text-xl`
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
