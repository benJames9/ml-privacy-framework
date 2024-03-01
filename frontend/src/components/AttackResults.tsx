import { AttackProgress } from "./AttackProgress";
import HBar from "./HBar";
import ReconstructedImage from "./ReconstructedImage";
import Stats from "./Stats";

interface AttackResultsProps {
  attackProgress: AttackProgress;
}

const AttackResults: React.FC<AttackResultsProps> = ({ attackProgress }) => {
  return (<div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
    <div className="flex flex-col items-center">
      <h1 className="text-4xl font-bold text-gray-100">Attack Statistics</h1>
      <Stats stats={attackProgress.statistics} />
      <HBar />
      <h1 className="text-4xl font-bold text-gray-100">Reconstructed Image</h1>
      <ReconstructedImage image={attackProgress.reconstructed_image} />
      <ReconstructedImage image={attackProgress.true_image} />
    </div>
  </div>);
};

export default AttackResults;