import { useState } from "react";
import CancelButton from "./CancelButton";
import HorizontalBar from "./ProgressBar";
import SaveTokenButton from "./SaveTokenButton";
import SuccessAlert from "./SuccessAlert";
import { copyToClipboard } from "@/utils/copyToClipboard";

interface AttackQueuedProps {
  queuedCurrent: number;
  queuedMax: number;
  onCancel: (requestToken: number) => void;
  params: {
    request_token: number
  }
}

const AttackQueued: React.FC<AttackQueuedProps> = ({ queuedCurrent, queuedMax, onCancel, params }) => {
  const [copied, setCopied] = useState<boolean>(false);

  const copyToken = () => {
    copyToClipboard(params.request_token.toString());
    setCopied(true);
  }

  return (
    <div className="flex flex-col items-center py-[25vh] bg-gradient-to-r from-black to-blue-950">
      <HorizontalBar min={0} max={Math.max(queuedMax + 1, 10)} current={Math.max(queuedMax + 1, 10) - queuedCurrent} text={`Position in queue: #${queuedCurrent}`} />
      <div className="flex mt-8 mb-8">
        <CancelButton
          onClick={() => onCancel(params.request_token)}
        />
        <SaveTokenButton
          onClick={copyToken}
        />
      </div>
      {copied && <SuccessAlert text="Token successfully copied to clipboard!" onClose={() => { setCopied(false) }} />}
    </div>
  );
}

export default AttackQueued;
