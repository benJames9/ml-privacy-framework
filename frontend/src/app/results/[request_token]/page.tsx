'use client'

import HBar from "@/components/HBar";
import Navbar from "@/components/Navbar";
import ReconstructedImage from "@/components/ReconstructedImage";
import Stats from "@/components/Stats";

import React, { useEffect, useState } from "react";
import HorizontalBar from "@/components/ProgressBar";

import { AttackStatistics } from "@/components/AttackStatistics";
import CancelButton from "@/components/CancelButton";

interface SearchParam {
  params: {
    request_token: number
  }
};

// TypeScript interface for AttackProgress
interface AttackProgress {
  current_iteration: number;
  max_iterations: number;
  current_restart: number;
  max_restarts: number;
  current_batch: number;
  max_batches: number;
  time_taken: number;
  statistics: AttackStatistics;
  reconstructed_image: string;
}

enum PageState {
  LOADING_SPINNER,
  LOADING_QUEUED,
  ATTACKING,
  FINAL_SCREEN
}

async function wait_ms(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const onCancel = async (requestToken: number) => {
  const res = await fetch(`/api/cancel/${requestToken}`, {
    method: 'POST',
  });

  if (res.ok) {
    window.location.href = "/";

    // Modify the browser history to prevent navigation back to this page
    window.history.replaceState(null, '', '/');
  } else {
    console.error('Failed to cancel attack');
  }
}

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
  const { request_token } = params;

  const [queuedMax, setQueuednMax] = useState(100);
  const [queuedCurrent, setQueuedCurrent] = useState(50);

  const [attackProgress, setAttackProgress] = useState<AttackProgress>({
    current_iteration: 0,
    max_iterations: 0,
    current_restart: 0,
    max_restarts: 0,
    current_batch: 0,
    max_batches: 0,
    time_taken: 0,
    statistics: {
      MSE: 0,
      PSNR: 0,
      SSIM: 0
    },
    reconstructed_image: ""
  });

  const [pageState, setPageState] = useState<PageState>(PageState.LOADING_SPINNER);

  useEffect(() => {
    const ws_url = construct_ws_url(`/ws/attack-progress/${request_token}`)
    const ws = new WebSocket(ws_url);

    ws.onmessage = async (e) => {
      const data = JSON.parse(e.data)
      console.log(data)
      switch (data.message_type) {
        case "PositionInQueue":
          setPageState(PageState.LOADING_QUEUED)
          setQueuednMax(data.total);
          setQueuedCurrent(data.position);
          break;
        case "AttackProgress":
          setQueuedCurrent(0);
          if (data.current_iteration !== data.max_iterations) {
            // let them see the full queue progress bar for a bit
            await wait_ms(500);
            setPageState(PageState.ATTACKING)
          }

          delete data.message_type;
          setAttackProgress(data);

          if (data.current_iteration === data.max_iterations) {
            // let them see the full attack progress bar for a bit
            await wait_ms(500);
            setPageState(PageState.FINAL_SCREEN);
          }
          break;
        case "error":
          if (pageState !== PageState.FINAL_SCREEN) {
            window.location.href = `/server-disconnect?error=${encodeURIComponent(data.error)}`;
          }
          break;
        default:
          break;
      }
    }

    // Cleanup function to close WebSocket connection
    return () => {
      ws.close();
    };
  }, [params.request_token]); // Dependency array to only re-run effect if params.request_token changes

  let content = null;
  switch (pageState) {
    case PageState.LOADING_SPINNER:
      content = <div className="flex min-h-screen py-[30vh] justify-center bg-gradient-to-r from-black to-blue-950">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white-900"></div>
      </div>
      break;
    case PageState.LOADING_QUEUED:
      content = <div className="flex min-h-screen flex-col items-center justify-between py-[25vh] bg-gradient-to-r from-black to-blue-950">
        <HorizontalBar min={0} max={Math.max(queuedMax + 1, 10)} current={Math.max(queuedMax + 1, 10) - queuedCurrent} text={`Position in queue: #${queuedCurrent}`} />
        <CancelButton
          onClick={() => onCancel(params.request_token)}
        />
      </div>
      break;
    case PageState.ATTACKING:
      content = <div className="flex min-h-screen flex-col items-center justify-between py-[25vh] bg-gradient-to-r from-black to-blue-950">
        <HorizontalBar
          current={attackProgress.current_iteration}
          min={0}
          max={attackProgress.max_iterations}
          text="Attacking..."
          color="bg-green-600"
        />
        <CancelButton
          onClick={() => onCancel(params.request_token)}
        />
      </div>
      break;
    case PageState.FINAL_SCREEN:
      content = <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
        <div className="flex flex-col items-center">
          <h1 className="text-4xl font-bold text-gray-100">Attack Statistics</h1>
          <Stats stats={attackProgress.statistics} />
          <HBar />
          <h1 className="text-4xl font-bold text-gray-100">Reconstructed Image</h1>
          <ReconstructedImage image={attackProgress.reconstructed_image} />
        </div>
      </div>
  }

  return (
    <main>
      <Navbar />
      {content}
    </main>
  );
}

export default ResultsPage;
