"use client";
import React, { useState } from 'react';

interface ModelSelectProps {
  models: string[];
  onChange: (model: string) => void;
}

const ModelSelect: React.FC<ModelSelectProps> = ({
  models,
  onChange,
}) => {
  const [internalSelectedModel, setInternalSelectedModel] = useState("");
  const handleModelSelect = (model: string) => {
    setInternalSelectedModel(model);
    onChange(model);
    const fileUpload = document.getElementById('upload-pt-header');
    fileUpload!.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div>
      <select
        value={internalSelectedModel}
        onChange={(e) => handleModelSelect(e.target.value)}
        className="bg-gray-900 text-white hover:bg-gray-600 border border-gray-300 text-gray-700 font-medium rounded-lg text-left inline-flex items-center text-base w-full py-4 px-4 justify-center text-xl"
      >
        {models.map((model) => (
          <option key={model} value={model} className="text-md">{model}</option>
        ))}
      </select>
    </div>
  );
};

export default ModelSelect;
