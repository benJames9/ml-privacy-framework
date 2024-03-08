import { AttackProgress } from "./AttackProgress";
import AttackResults from "./AttackResults"

interface AttackResultsPageProps {
  attackProgress: AttackProgress;
}

const AttackResultsPage: React.FC<AttackResultsPageProps> = ({ attackProgress }) => {
  return (
    <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
      <AttackResults attackProgress={attackProgress} />
    </div>
  );
};

export default AttackResultsPage;
