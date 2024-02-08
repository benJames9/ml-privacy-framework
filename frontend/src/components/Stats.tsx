interface StatsProps {
  stats: { [key: string]: number };
}

const Stats: React.FC<StatsProps> = ({ stats }) => {
  return (
    <div className="inline-flex rounded-md shadow-sm mt-10" role="group">
      <div className="px-8 py-6 text-gray-200 bg-gray-800 border border-gray-900 rounded-s-lg text-center">
        <h1 className="text-4xl font-bold text-white mb-4">{stats["MSE"]}</h1>
        <h3 className="text-2xl font-bold text-gray-300 mb-4">MSE</h3>
        <p className="text-sm text-gray-400">Mean Square Error</p>
      </div>
      <div className="px-8 py-6 text-gray-200 bg-gray-800 border-t border-b border-gray-900 text-center">
        <h1 className="text-4xl font-bold text-white mb-4">{stats["PSNR"]}</h1>
        <h3 className="text-2xl font-bold text-gray-300 mb-4">PSNR</h3>
        <p className="text-sm text-gray-400">Peak Signal-to-Noise Ratio</p>
      </div>
      <div className="px-8 py-6 text-gray-200 bg-gray-800 border border-gray-900 rounded-e-lg text-center">
        <h1 className="text-4xl font-bold text-white mb-4">{stats["SSIM"]}</h1>
        <h3 className="text-2xl font-bold text-gray-300 mb-4">SSIM</h3>
        <p className="text-sm text-gray-400">Structural Similarity Index</p>
      </div>
    </div>
  );
};

export default Stats;