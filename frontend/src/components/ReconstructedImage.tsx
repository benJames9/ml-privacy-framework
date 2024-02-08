interface ReconstructedImageProps {
  image: string;
}

const ReconstructedImage: React.FC<ReconstructedImageProps> = ({ image }) => {
  return (
    <div className="flex flex-col items-center">
      <img src={image} alt="reconstructed" className="mt-8" />
    </div>
  );
}

export default ReconstructedImage;