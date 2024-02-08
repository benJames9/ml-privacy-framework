import Navbar from "@/components/Navbar";
import Stats from "@/components/Stats";

const ResultsPage: React.FC = () => {
  const stats = { "MSE": 0.1, "PSNR": 0.2, "SSIM": 0.3 }; // Replace with backend response

  return (
    <main>
      <Navbar />
      <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
        <div className="flex flex-col items-center">
          <h1 className="text-4xl font-bold text-gray-400">Attack Statistics</h1>
          <Stats stats={stats} />
        </div>
      </div>
    </main>
  );
}

export default ResultsPage;