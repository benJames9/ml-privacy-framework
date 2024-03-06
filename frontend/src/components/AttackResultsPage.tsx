import { AttackProgress } from "./AttackProgress";
import AttackResults from "./AttackResults"
import HBar from "./HBar";
import Stats from "./Stats";

interface AttackResultsPageProps {
  attackProgress: AttackProgress;
  modality: string;
}

const AttackResultsPage: React.FC<AttackResultsPageProps> = ({ attackProgress, modality }) => {
  return (<div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
    <AttackResults modality={modality} attackProgress={attackProgress} />
  </div>);
};

export default AttackResultsPage;