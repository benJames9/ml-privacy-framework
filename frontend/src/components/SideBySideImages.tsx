import { AttackProgress } from "./AttackProgress";
import ReconstructedImage from "./ReconstructedImage";
import HBar from "./HBar";

interface SideBySideImagesProps {
    attackProgress: AttackProgress;
}

function images_exist(attackProgress: AttackProgress) {
  return !!attackProgress.reconstructed_image && attackProgress.reconstructed_image != "" &&
         !!attackProgress.true_image && attackProgress.true_image != ""
}

export const SideBySideImages: React.FC<SideBySideImagesProps> = ({ attackProgress }) => {
    return (
    images_exist(attackProgress) &&
    <div className="text-center">
        <HBar />
        <h1 className="text-4xl font-bold text-gray-100">Reconstructed Image</h1>
        <div className="flex">
          <ReconstructedImage image={attackProgress.reconstructed_image} />
          <ReconstructedImage image={attackProgress.true_image} />
        </div>
      </div>
    )
}