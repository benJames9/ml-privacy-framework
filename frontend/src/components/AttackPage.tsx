import { useState } from "react";
import { AttackProgress } from "./AttackProgress";
import CancelButton from "./CancelButton";
import HorizontalBar from "./ProgressBar";
import TimeEstimate from "./TimeEstimate";
import SaveTokenButton from "./SaveTokenButton";
import SuccessAlert from "./SuccessAlert";
import AttackResults from "./AttackResults";

interface AttackPageProps {
  attackProgress: AttackProgress;
  startTime: number | null;
  previousTimes: number[];
  onCancel: (requestToken: number) => void;
  params: {
    request_token: number
  }
}

const AttackPage: React.FC<AttackPageProps> = ({ modality, attackProgress, startTime, previousTimes, onCancel, params }) => {
  const [copied, setCopied] = useState<boolean>(false);

  const copyToken = () => {
    navigator.clipboard.writeText(params.request_token.toString());
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  }

  return (
    <div className="flex min-h-screen flex-col items-center py-[5vh] bg-gradient-to-r from-black to-blue-950">
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
      <div className="flex mt-8 mb-8">
        <CancelButton
          onClick={() => onCancel(params.request_token)}
        />
        <SaveTokenButton
          onClick={copyToken}
        />
      </div>
      {copied && <SuccessAlert text="Token successfully copied to clipboard!" onClose={() => { setCopied(false) }} />}
      <div className="flex flex-col items-center pt-[5vh]">
        <AttackResults modality={modality} attackProgress={attackProgress} />
      </div>
    </div>
  )
}

export default AttackPage;
