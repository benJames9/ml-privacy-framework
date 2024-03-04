import CancelButton from "./CancelButton";
import HorizontalBar from "./ProgressBar";
import SaveTokenButton from "./SaveTokenButton";

interface AttackQueuedProps {
  queuedCurrent: number;
  queuedMax: number;
  onCancel: (requestToken: number) => void;
  params: {
    request_token: number
  }

}

const AttackQueued: React.FC<AttackQueuedProps> = ({ queuedCurrent, queuedMax, onCancel, params }) => {

  return (
    <div className="flex flex-col items-center py-[25vh] bg-gradient-to-r from-black to-blue-950">
      <HorizontalBar min={0} max={Math.max(queuedMax + 1, 10)} current={Math.max(queuedMax + 1, 10) - queuedCurrent} text={`Position in queue: #${queuedCurrent}`} />
      <div className="flex mt-8">
        <CancelButton
          onClick={() => onCancel(params.request_token)}
        />
        <SaveTokenButton
          token={params.request_token}
        />
      </div>
    </div>
  );
}

export default AttackQueued;