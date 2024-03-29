'use client'

import Navbar from "@/components/Navbar";

import React, { useEffect, useState } from "react";

import { AttackProgress } from "@/components/AttackProgress";
import AttackLoading from "@/components/AttackLoading";
import AttackQueued from "@/components/AttackQueued";
import AttackPage from "@/components/AttackPage";
import AttackResultsPage from "@/components/AttackResultsPage";

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

function does_progress_update_have_images(progress: AttackProgress) {
  return !(progress.reconstructed_image == "" || !progress.reconstructed_image) &&
    !(progress.true_image == "" || !progress.true_image)
}

function does_progress_update_have_stats(progress: AttackProgress) {
  return Object.values(progress.statistics).reduce((acc, curr) => acc ||= curr != 0, false)
}

const ResultsPage: React.FC<SearchParam> = ({ params }) => {
  const { request_token } = params;

  const [queuedMax, setQueuednMax] = useState(100);
  const [queuedCurrent, setQueuedCurrent] = useState(50);

  const [attackProgress, setAttackProgress] = useState<AttackProgress>({
    attack_type: "",
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
      SSIM: 0,
      ACC: 0,
      GBLEU: 0,
      FMSE: 0
    },
    true_image: "",
    reconstructed_image: "",
    reconstructed_images_archive: "",
    attack_start_time_s: 0,
    true_text: "",
    reconstructed_text: "",
    mia_stats: {
      likelihood_ratio: 0
    }
  });
  const [currentIteration, setCurrentIteration] = useState<number>(0);
  const [startTime, setStartTime] = useState<number | null>(null);

  const [pageState, setPageState] = useState<PageState>(PageState.LOADING_SPINNER);
  const [attackModality, setAttackModality] = useState<"images" | "text">("images");

  useEffect(() => {
    const newIteration = attackProgress.current_iteration + attackProgress.current_restart * attackProgress.max_iterations;
    if (newIteration !== currentIteration) {
      setCurrentIteration(newIteration);
    }
    setStartTime(performance.now());
  }, [attackProgress]);

  useEffect(() => {
    const ws_url = construct_ws_url(`/ws/attack-progress/${request_token}`)
    const ws = new WebSocket(ws_url);

    let cached_true_image = attackProgress.true_image
    let reconstructed_image = attackProgress.reconstructed_image
    let statistics = attackProgress.statistics

    ws.onmessage = async (e) => {
      const data = JSON.parse(e.data)
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

          if (does_progress_update_have_stats(data)) {
            if (does_progress_update_have_images(data)) {
              cached_true_image = data.true_image;
              reconstructed_image = data.reconstructed_image;
            }
            statistics = data.statistics;
          }

          const augmented_update = {
            ...data,
            true_image: cached_true_image,
            reconstructed_image,
            statistics
          }

          setAttackProgress(augmented_update);

          if (data.reconstructed_text !== "") {
            setAttackModality("text");
          }

          if (data.current_iteration === data.max_iterations
            && data.current_restart === data.max_restarts) {
            // let them see the full attack progress bar for a bit
            await wait_ms(500);
            setPageState(PageState.FINAL_SCREEN);

            // since we're only now displaying those components
            // we need to set the data that they should have again
            // since they wouldn't have had the data set before they were enabled
            setAttackProgress(augmented_update);
          }

          break;
        case "error":
          if (pageState !== PageState.FINAL_SCREEN) {
            window.location.href = `/server-disconnect?error=${encodeURIComponent(data.error_message)}`;
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
        onCancel={onCancel}
        params={params}
      />
      break;
    case PageState.FINAL_SCREEN:
      content = <AttackResultsPage attackProgress={attackProgress} />
  }

  return (
    <main>
      <Navbar />
      {content}
    </main>
  );
}

export default ResultsPage;
