import { AttackProgress } from "./AttackProgress";
import { SideBySideImages } from "./SideBySideImages"
import Stats from "./Stats";

interface AttackResultsProps {
  attackProgress: AttackProgress;
}

const AttackResults: React.FC<AttackResultsProps> = ({ attackProgress }) => {
  return (
    <div className="flex flex-col items-center">
      <Stats stats={attackProgress.statistics} attack={attackProgress.attack_type} />
      {attackProgress.attack_type === "invertinggradients" && <div>
        <SideBySideImages attackProgress={attackProgress} />
      </div>}
    </div>);
};

export default AttackResults;