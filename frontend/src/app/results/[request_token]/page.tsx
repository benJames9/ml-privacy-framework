'use client'

import HBar from "@/components/HBar";
import Navbar from "@/components/Navbar";
import ReconstructedImage from "@/components/ReconstructedImage";
import Stats from "@/components/Stats";

import React, { useEffect } from "react";

interface SearchParam {
  params: {
    request_token: number
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

  const { request_token } = params;

  useEffect(() => {
    const ws_url = construct_ws_url(`/ws/attack-progress/${request_token}`)
    const ws = new WebSocket(ws_url);

    ws.onopen = () => {
      // TODO: receive updates from here and update state accordingly
    };

    ws.onmessage = (e) => {
      console.log(e.data)
    }

    // Cleanup function to close WebSocket connection
    return () => {
      ws.close();
    };
  }, [params.request_token]); // Dependency array to only re-run effect if params.request_token changes

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
