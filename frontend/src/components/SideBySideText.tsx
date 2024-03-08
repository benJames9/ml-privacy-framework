import { AttackProgress } from "./AttackProgress";
import HBar from "./HBar"

interface SideBySideTextProps {
  attackProgress: AttackProgress;

}

const SideBySideText: React.FC<SideBySideTextProps> = ({ attackProgress }) => {
  return (
    <div className="text-center">
      <HBar />
      <h1 className="text-4xl font-bold text-gray-100">Reconstructed Text</h1>
      <div className="flex">
        <p className="text-gray-100">{attackProgress.reconstructed_text}</p>
        <p className="text-gray-100">{attackProgress.true_text}</p>
      </div>
    </div>
  )
}

export default SideBySideText;