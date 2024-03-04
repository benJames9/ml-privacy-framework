'use client'

import Navbar from "@/components/Navbar";

import React, { useEffect, useState } from "react";

import { AttackProgress } from "@/components/AttackProgress";
import AttackLoading from "@/components/AttackLoading";
import AttackQueued from "@/components/AttackQueued";
import AttackPage from "@/components/AttackPage";
import AttackResults from "@/components/AttackResults";

interface SearchParam {
  params: {
    request_token: number
  }
};

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
    true_image: "",
    reconstructed_image: ""
  });
  const [currentIteration, setCurrentIteration] = useState<number>(0);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [previousTimes, setPreviousTimes] = useState<number[]>([]);

  const [pageState, setPageState] = useState<PageState>(PageState.FINAL_SCREEN);
  const [attackModality, setAttackModality] = useState<"image" | "text">("image");

  useEffect(() => {
    const newIteration = attackProgress.current_iteration + attackProgress.current_restart * attackProgress.max_iterations;
    if (newIteration !== currentIteration) {
      setCurrentIteration(newIteration);
      if (startTime) {
        setPreviousTimes([...previousTimes, (performance.now() - startTime) / 1000]);
      }
    }
    setStartTime(performance.now());
  }, [attackProgress]);

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

          if (data.current_iteration === data.max_iterations
            && data.current_restart === data.max_restarts) {
            if (data.true_image === "" && data.reconstructed_image === "") {
              setAttackModality("text");
            }
            
            // let them see the full attack progress bar for a bit
            await wait_ms(500);
            setPageState(PageState.FINAL_SCREEN);

            // since we're only now displaying those components
            // we need to set the data that they should have again
            // since they wouldn't have had the data set before they were enabled
            setAttackProgress(data);
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
      content = <AttackLoading />
      break;
    case PageState.LOADING_QUEUED:
      content = <AttackQueued
        queuedCurrent={queuedCurrent}
        queuedMax={queuedMax}
        onCancel={onCancel}
        params={params}
      />
      break;
    case PageState.ATTACKING:
      content = <AttackPage attackProgress={attackProgress}
        startTime={startTime}
        previousTimes={previousTimes}
        onCancel={onCancel}
        params={params}
      />
      break;
    case PageState.FINAL_SCREEN:
      content = <AttackResults attackProgress={attackProgress} modality={attackModality} />
  }

  return (
    <main>
      <Navbar />
      {content}
    </main>
  );
}

export default ResultsPage;
