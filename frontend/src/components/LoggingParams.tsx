"use client";
import React from 'react';
import NumberInput from './NumberInput';

interface LoggingParamsProps {
  handleLoggingParamsChange: (value: string) => void;
}

const LoggingParams: React.FC<LoggingParamsProps> = ({ handleLoggingParamsChange }) => {
  return (
    <div>
      <NumberInput
        label="Callback Interval:"
        onChange={(e) => handleLoggingParamsChange(e.target.value)}
      />
    </div>
  );

};

export default LoggingParams;