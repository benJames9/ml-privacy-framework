import { AttackProgress } from "./AttackProgress";
import ReconstructedImage from "./ReconstructedImage";

interface SideBySideImagesProps {
    attackProgress: AttackProgress;
}

export const SideBySideImages: React.FC<SideBySideImagesProps> = ({ attackProgress }) => {
    return (
    <div class="text-center">
        <h1 className="text-4xl font-bold text-gray-100">Reconstructed Image</h1>
        <div class="flex">
          <ReconstructedImage image={attackProgress.reconstructed_image} />
          <ReconstructedImage image={attackProgress.true_image} />
        </div>
      </div>
    )
}