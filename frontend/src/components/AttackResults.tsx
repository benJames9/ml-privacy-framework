import { AttackProgress } from "./AttackProgress";
import { SideBySideImages } from "./SideBySideImages"
import Stats from "./Stats";

interface AttackResultsProps {
  attackProgress: AttackProgress;
}

const AttackResults: React.FC<AttackResultsProps> = ({ attackProgress }) => {
  const attack = attackProgress.attack_type;

  const getColour = () => {
    const likelihoodRatio = attackProgress.mia_stats.likelihood_ratio;
    if (likelihoodRatio > 1) {
      return "bg-green-900";
    } else if (likelihoodRatio < 1) {
      return "bg-red-900";
    } else {
      return "bg-gray-800";
    }
  }

  const getMiaResult = () => {
    const likelihoodRatio = attackProgress.mia_stats.likelihood_ratio;
    if (likelihoodRatio > 1) {
      return "It's likely that the target point was a member of the training dataset.";
    } else if (likelihoodRatio < 1) {
      return "It's unlikely that the target point was a member of the training dataset.";
    } else {
      return "It's equally likely that the target point was a member/non-member of the training dataset.";
    }
  }

  return (
    <div className="flex flex-col items-center">
      {attack === "mia"
        ?
        <div className="flex flex-col items-center">
          <div className="inline-flex rounded-md shadow-sm mt-16 text-center">
            <div className={`px-8 py-5 text-gray-200 ${getColour()} border border-gray-900 rounded-md`}>
              <h1 className="text-4xl font-bold text-white mb-4">{attackProgress.mia_stats.likelihood_ratio.toFixed(2)}</h1>
              <h3 className="text-2xl text-gray-300">Likelihood Ratio</h3>
            </div>
          </div>
          <h3 className="text-2xl text-bold text-gray-200 mt-16">{getMiaResult()}</h3>
        </div>
        : <Stats stats={attackProgress.statistics} attack={attack} />
      }
      {attack === "invertinggradients" && <div>
        <SideBySideImages attackProgress={attackProgress} />
      </div>}
    </div>);
};

export default AttackResults;