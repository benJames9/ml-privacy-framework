import React from 'react';

interface HorizontalBarProps {
  min: number;
  max: number;
  current: number;
  color?: string;
  text: string
}

const HorizontalBar: React.FC<HorizontalBarProps> = ({ min, max, current, color = 'bg-blue-500', text }) => {
  const percentage = ((current - min) / (max - min)) * 100;

  return (
    <div className="text-center w-4/5 min-w-[300px]">
      <h1 className="text-white text-2xl mb-4">{text}</h1>
      <div className="h-[15vh] bg-gray-300 rounded-3xl overflow-hidden">
        <div
          style={{ width: `${percentage}%` }}
          className={`h-full ${color} rounded-3xl transition-all duration-500 ease-in-out`}
        />
      </div>
    </div>
  );
};

export default HorizontalBar;
