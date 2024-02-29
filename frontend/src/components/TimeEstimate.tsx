import { useEffect, useState } from "react";
import { AttackProgress } from "./AttackProgress";

interface TimeEstimateProps {
  attackProgress: AttackProgress;
  startTime: number | null;
  previousTimes: number[];
}

const TimeEstimate: React.FC<TimeEstimateProps> = ({ attackProgress, startTime, previousTimes }) => {
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [currentIteration, setCurrentIteration] = useState<number>(0);

  const totalIterations = attackProgress.max_iterations * attackProgress.max_restarts;

  useEffect(() => {
    if (!attackProgress || !startTime || previousTimes.length === 0) return;

    const currentIterationTime = performance.now() - startTime;
    const averageTimePerIteration = previousTimes.reduce((a, b) => a + b, 0) / previousTimes.length;

    const currentIteration = attackProgress.current_iteration + attackProgress.current_restart * attackProgress.max_iterations;
    const remainingIterations = totalIterations - currentIteration;

    if (currentIteration <= totalIterations) {
      setCurrentIteration(currentIteration);
    }
    
    const timeEstimate = remainingIterations * averageTimePerIteration - currentIterationTime;
    if (timeEstimate > 0) {
      setTimeRemaining(timeEstimate);
    }
  }, [attackProgress, startTime, previousTimes]);

  const formatTime = (time: number) => {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600) / 60);
    const seconds = Math.floor(time % 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    }
    if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    }
    return `${seconds}s`;
  };

  return (
    <div>
      <p>Iteration: {currentIteration}/{totalIterations}</p>
      <p>Estimated time remaining: ~{formatTime(timeRemaining)}</p>
    </div>
  )
};

export default TimeEstimate;
