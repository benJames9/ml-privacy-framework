import HBar from "@/components/HBar";
import Navbar from "@/components/Navbar";
import ReconstructedImage from "@/components/ReconstructedImage";
import Stats from "@/components/Stats";

const ResultsPage: React.FC = () => {
  const stats = { "MSE": 0.1164, "PSNR": 9.40, "SSIM": 5.184e-03 }; // Replace with backend response

  return (
    <main>
      <Navbar />
      <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
        <div className="flex flex-col items-center">
          <h1 className="text-4xl font-bold text-gray-400">Attack Statistics</h1>
          <Stats stats={stats} />
          <HBar />
          <h1 className="text-4xl font-bold text-gray-400">Reconstructed Image</h1>
          <ReconstructedImage image="/demo.jpg" /> {/* Replace with backend response*/}
        </div>
      </div>
    </main>
  );
}

export default ResultsPage;