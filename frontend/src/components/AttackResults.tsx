import { AttackProgress } from "./AttackProgress";
import { SideBySideImages } from "./SideBySideImages"
import HBar from "./HBar";
import Stats from "./Stats";

interface AttackResultsProps {
  attackProgress: AttackProgress;
  modality: string;
}

const AttackResults: React.FC<AttackResultsProps> = ({ attackProgress, modality }) => {
  return (
    <div className="flex flex-col items-center">
      <h1 className="text-4xl font-bold text-gray-100">Attack Statistics</h1>
      <Stats stats={attackProgress.statistics} modality={modality} />
      {modality === "images" && <div>
        <HBar />
        <SideBySideImages attackProgress={attackProgress} />
      </div>}
    </div>);
};

export default AttackResults;