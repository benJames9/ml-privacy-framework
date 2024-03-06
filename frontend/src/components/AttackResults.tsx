import { AttackProgress } from "./AttackProgress";
import { SideBySideImages } from "./SideBySideImages"
import Stats from "./Stats";

interface AttackResultsProps {
  attackProgress: AttackProgress;
  modality: string;
}

const AttackResults: React.FC<AttackResultsProps> = ({ attackProgress, modality }) => {
  return (
    <div className="flex flex-col items-center">
      <Stats stats={attackProgress.statistics} modality={modality} />
      {modality === "images" && <div>
        <SideBySideImages attackProgress={attackProgress} />
      </div>}
    </div>);
};

export default AttackResults;