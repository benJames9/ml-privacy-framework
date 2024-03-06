interface ReconstructedImageProps {
  image: string;
  mimeType?: string;
}

const ReconstructedImage: React.FC<ReconstructedImageProps> = ({ image, mimeType = "image/jpg" }) => {
  return (
    <div className="flex-auto p-5 items-center">
      <img src={`data:${mimeType};base64,${image}`} alt="reconstructed" className="mt-8" />
    </div>
  );
}

export default ReconstructedImage;
