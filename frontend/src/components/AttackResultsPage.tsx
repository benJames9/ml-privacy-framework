import { AttackProgress } from "./AttackProgress";
import AttackResults from "./AttackResults"
import DownloadLink from "./DownloadLink";

interface AttackResultsPageProps {
  attackProgress: AttackProgress;
}

const AttackResultsPage: React.FC<AttackResultsPageProps> = ({ attackProgress }) => {
  return (
    <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
      <AttackResults attackProgress={attackProgress} />
      {attackProgress.attack_type === "invertinggradients" && <div className="m-3">
        <DownloadLink base64Zip={attackProgress.reconstructed_images_archive} fileName="reconstructed_data.zip" />
      </div>
      }
    </div>
  );
};

export default AttackResultsPage;
