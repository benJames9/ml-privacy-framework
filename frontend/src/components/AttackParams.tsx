"use client";
import React from 'react';
import NumberInput from './NumberInput';

interface AttackParamsProps {
  handleAttackParamsChange: (field: string, value: string) => void;
}

const AttackParams: React.FC<AttackParamsProps> = ({ handleAttackParamsChange }) => {
  return (
    <div>
      <NumberInput
        label="Number of restarts"
        onChange={(e) => handleAttackParamsChange("restarts", e.target.value)}
        isRequired={true}
      />
      <NumberInput
        label="Step size"
        onChange={(e) => handleAttackParamsChange("stepSize", e.target.value)}
        isRequired={true}
      />
      <NumberInput
        label="Maximum iterations"
        onChange={(e) => handleAttackParamsChange("maxIterations", e.target.value)}
        isRequired={true}
      />
    </div>
  );

};

export default AttackParams;
