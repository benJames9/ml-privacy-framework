"use client";
import React, { useState } from 'react';
import NumberInput from './NumberInput';

const LoggingParams: React.FC = () => {
  const [callbackInterval, setCallbackInterval] = useState<number>(0);

  const handleInputChange = (value: string) => {
    console.log(value);
    setCallbackInterval(parseInt(value));
  }

  return (
    <div>
      <NumberInput
        label="Callback Interval:"
        onChange={(e) => handleInputChange(e.target.value)}
      />
    </div>
  );

};

export default LoggingParams;