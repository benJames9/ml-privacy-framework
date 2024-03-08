interface LoadingIconProps {
  size: string;
}
const LoadingIcon: React.FC<LoadingIconProps> = ({ size }) => {
  return (
    <div>
      {size === "small" && <div className="relative" id="loading-icon">
        <div className="h-12 w-12 rounded-full border-t-4 border-b-4 border-gray-200"></div>
        <div className="absolute top-0 left-0 h-12 w-12 rounded-full border-t-4 border-b-4 border-blue-500 animate-spin">
        </div>
      </div>}
      {size === "big" && <div className="relative" id="loading-icon">
        <div className="h-32 w-32 rounded-full border-t-8 border-b-8 border-gray-200"></div>
        <div className="absolute top-0 left-0 h-32 w-32 rounded-full border-t-8 border-b-8 border-blue-500 animate-spin">
        </div>
      </div>}

    </div>
  );
}

export default LoadingIcon;
