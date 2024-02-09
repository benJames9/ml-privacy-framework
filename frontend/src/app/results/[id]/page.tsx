'use client'

import HBar from "@/components/HBar";
import Navbar from "@/components/Navbar";
import ReconstructedImage from "@/components/ReconstructedImage";
import Stats from "@/components/Stats";

import React, { useEffect } from "react";

interface SearchParam {
  params: {
    id: number
  }
};

/**
 * Construct a valid websocket URL given an endpoint
 * @param {string} endpoint - The endpoint (starting with a "/")
 * @returns {string} The resultant valid URL
 */
function construct_ws_url(endpoint: string) {
  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const wsHost = window.location.hostname;
  return `${wsScheme}://${wsHost}${endpoint}`
}

const ResultsPage: React.FC<SearchParam> = ({ params }) => {
  const stats = { "MSE": 0.1164, "PSNR": 9.40, "SSIM": 5.184e-03 }; // Replace with backend response

  useEffect(() => {
    const ws = new WebSocket(construct_ws_url("/ws"));

    ws.onopen = () => {
      // Do stuff
    };

    // Cleanup function to close WebSocket connection
    return () => {
      ws.close();
    };
  }, [params.id]); // Dependency array to only re-run effect if params.id changes

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
