"use client";
import React, { useState } from 'react';

interface ModelSelectProps {
  models: string[];
  selectedModel?: string;
}

const ModelSelect: React.FC<ModelSelectProps> = ({
  models,
  selectedModel,
}) => {
  const [internalSelectedModel, setInternalSelectedModel] = useState<string>(
    selectedModel || ''
  );

  const handleModelSelect = (model: string) => {
    setInternalSelectedModel(model);
    console.log(`Selected model: ${model}`);
    console.log("Hello");
  };

  return (
    <div className="grid grid-cols-2 gap-8">
      {models.map((model) => (
        <button
          key={model}
          type="button"
          className={
            "bg-gray-900 text-white hover:bg-gray-600 border border-gray-300 text-gray-700 focus:ring-4 focus:ring-blue-500 font-medium rounded-lg text-center inline-flex items-center px-5 py-4 text-base w-full justify-center min-w-48 h-32 min-w-32 text-xl"
          }
          onClick={() => handleModelSelect(model)}
        >
          <span>{model}</span>
        </button>
      ))}
    </div>
  );
};

export default ModelSelect;
