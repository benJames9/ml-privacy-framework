"use client";
import React, { useState } from 'react';
import NumberInput from './NumberInput';

const AttackParams: React.FC = () => {
  const [numRestarts, setNumRestarts] = useState<number>(0);
  const [stepSize, setStepSize] = useState<number>(0);
  const [maxIterations, setMaxIterations] = useState<number>(0);

  const handleInputChange = (field: string, value: string) => {
    switch (field) {
      case "restarts":
        setNumRestarts(parseInt(value));
        break;
      case "stepSize":
        setStepSize(parseInt(value));
        break;
      case "maxIterations":
        setMaxIterations(parseInt(value));
        break;
      default:
        break;
    }
  }

  return (
    <div>
      <NumberInput
        label="Number of restarts:"
        onChange={(e) => handleInputChange("restarts", e.target.value)}
      />
      <NumberInput
        label="Step size:"
        onChange={(e) => handleInputChange("stepSize", e.target.value)}
      />
      <NumberInput
        label="Maximum iterations:"
        onChange={(e) => handleInputChange("maxIterations", e.target.value)}
      />
    </div>
  );

};

export default AttackParams;