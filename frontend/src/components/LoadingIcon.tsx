interface LoadingIconProps {
  size: number;
  borderSize: number;
}
const LoadingIcon: React.FC<LoadingIconProps> = ({ size, borderSize}) => {
  return (
    <div className="relative" id="loading-icon">
      <div className={`h-${size} w-${size} rounded-full border-t-${borderSize} border-b-${borderSize} border-gray-200`}></div>
      <div className={`absolute top-0 left-0 h-${size} w-${size} rounded-full border-t-${borderSize} border-b-${borderSize} border-blue-500 animate-spin`}>
      </div>
    </div>
  );
}

export default LoadingIcon;