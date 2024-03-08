import { useState } from "react";
import { AttackProgress } from "./AttackProgress";
import CancelButton from "./CancelButton";
import HorizontalBar from "./ProgressBar";
import TimeEstimate from "./TimeEstimate";
import SaveTokenButton from "./SaveTokenButton";
import SuccessAlert from "./SuccessAlert";
import AttackResults from "./AttackResults";
import { copyToClipboard } from "@/utils/copyToClipboard";

interface AttackPageProps {
  attackProgress: AttackProgress;
  startTime: number | null;
  onCancel: (requestToken: number) => void;
  params: {
    request_token: number
  }
}

const AttackPage: React.FC<AttackPageProps> = ({ attackProgress, startTime, onCancel, params }) => {
  const [copied, setCopied] = useState<boolean>(false);

  const copyToken = () => {
    copyToClipboard(params.request_token.toString());
    setCopied(true);
  }

  return (
    <div className="flex min-h-screen flex-col items-center py-[5vh] bg-gradient-to-r from-black to-blue-950">
      <HorizontalBar
        current={attackProgress.current_iteration + ((attackProgress.current_restart || 0) * (attackProgress.max_iterations || 0))}
        min={0}
        max={(attackProgress.max_restarts || 1) * attackProgress.max_iterations}
        text="Attacking..."
        color="bg-green-600"
      />
      <TimeEstimate
        attackProgress={attackProgress}
        startTime={startTime}
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
      {attackProgress.attack_type === "invertinggradients" && <div className="flex flex-col items-center pt-[5vh]">
        <AttackResults attackProgress={attackProgress} />
      </div>}
    </div>
  )
}

export default AttackPage;
