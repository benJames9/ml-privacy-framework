import { AttackStatistics } from "./AttackStatistics";

interface StatsProps {
  stats: AttackStatistics;
  decimalPlaces?: number;
  modality: string;
}

const Stats: React.FC<StatsProps> = ({ stats, decimalPlaces = 4, modality }) => {
  return (
    <div>
      {modality === "image" && <div className="inline-flex rounded-md shadow-sm mt-10" role="group">
        <div className="px-8 py-6 text-gray-200 bg-gray-800 border border-gray-900 rounded-s-lg text-center">
          <h1 className="text-4xl font-bold text-white mb-4">{stats.MSE!.toFixed(decimalPlaces)}</h1>
          <h3 className="text-2xl font-bold text-gray-300 mb-4">MSE</h3>
          <p className="text-sm text-gray-400">Mean Square Error</p>
        </div>
        <div className="px-8 py-6 text-gray-200 bg-gray-800 border-t border-b border-gray-900 text-center">
          <h1 className="text-4xl font-bold text-white mb-4">{stats.PSNR!.toFixed(decimalPlaces)}</h1>
          <h3 className="text-2xl font-bold text-gray-300 mb-4">PSNR</h3>
          <p className="text-sm text-gray-400">Peak Signal-to-Noise Ratio</p>
        </div>
        <div className="px-8 py-6 text-gray-200 bg-gray-800 border border-gray-900 rounded-e-lg text-center">
          <h1 className="text-4xl font-bold text-white mb-4">{stats.SSIM!.toFixed(decimalPlaces)}</h1>
          <h3 className="text-2xl font-bold text-gray-300 mb-4">SSIM</h3>
          <p className="text-sm text-gray-400">Structural Similarity Index</p>
        </div>
      </div>
      }
      {modality === "text" && <div className="inline-flex rounded-md shadow-sm mt-10" role="group">
        <div className="px-8 py-6 text-gray-200 bg-gray-800 border border-gray-900 rounded-s-lg text-center">
          <h1 className="text-4xl font-bold text-white mb-4">{stats.ACC!.toFixed(decimalPlaces)}</h1>
          <h3 className="text-2xl font-bold text-gray-300 mb-4">ACC</h3>
          <p className="text-sm text-gray-400">Token Accuracy</p>
        </div>
        <div className="px-8 py-6 text-gray-200 bg-gray-800 border-t border-b border-gray-900 text-center">
          <h1 className="text-4xl font-bold text-white mb-4">{stats.GBLEU!.toFixed(decimalPlaces)}</h1>
          <h3 className="text-2xl font-bold text-gray-300 mb-4">G-BLEU</h3>
          <p className="text-sm text-gray-400">Google BLEU</p>
        </div>
        <div className="px-8 py-6 text-gray-200 bg-gray-800 border border-gray-900 rounded-e-lg text-center">
          <h1 className="text-4xl font-bold text-white mb-4">{stats.FMSE!.toFixed(decimalPlaces)}</h1>
          <h3 className="text-2xl font-bold text-gray-300 mb-4">FMSE</h3>
          <p className="text-sm text-gray-400">Feature Mean Square Error</p>
        </div>
      </div>
      }
    </div>
  );
};

export default Stats;
