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
      <div className="grid grid-cols-2 gap-8 mt-8">
        <div className="bg-gray-700 p-8 rounded-lg whitespace-pre-wrap break-words shadow-lg max-w-sm">
          <h3 className="text-3xl text-blue-400 font-bold mb-4">Original</h3>
          <p className="text-gray-100 text-xl">{attackProgress.true_text}</p>
        </div>
        <div className="bg-gray-700 p-8 rounded-lg whitespace-pre-wrap break-words shadow-lg max-w-sm">
          <h3 className="text-3xl text-blue-400 font-bold mb-4">Reconstructed</h3>
          <p className="text-gray-100 text-xl">{attackProgress.reconstructed_text}</p>
        </div>
      </div>
    </div>
  )
}

export default SideBySideText;
