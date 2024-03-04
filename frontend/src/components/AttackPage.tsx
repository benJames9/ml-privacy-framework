import { AttackProgress } from "./AttackProgress";
import CancelButton from "./CancelButton";
import HorizontalBar from "./ProgressBar";
import TimeEstimate from "./TimeEstimate";

interface AttackPageProps {
  attackProgress: AttackProgress;
  startTime: number | null;
  previousTimes: number[];
  onCancel: (requestToken: number) => void;
  params: {
    request_token: number
  }
}

const AttackPage: React.FC<AttackPageProps> = ({ attackProgress, startTime, previousTimes, onCancel, params }) => {
  return (
    <div className="flex min-h-screen flex-col items-center justify-between py-[25vh] bg-gradient-to-r from-black to-blue-950">
      <HorizontalBar
        current={attackProgress.current_iteration + ((attackProgress.current_restart) * attackProgress.max_iterations)}
        min={0}
        max={attackProgress.max_restarts * attackProgress.max_iterations}
        text="Attacking..."
        color="bg-green-600"
      />
      <TimeEstimate
        attackProgress={attackProgress}
        startTime={startTime}
        previousTimes={previousTimes}
      />
      <CancelButton
        onClick={() => onCancel(params.request_token)}
      />
    </div>
  )
}

export default AttackPage;
