import { AttackStatistics } from "./AttackStatistics";

// TypeScript interface for AttackProgress
export interface AttackProgress {
  current_iteration: number;
  max_iterations: number;
  current_restart: number;
  max_restarts: number;
  current_batch: number;
  max_batches: number;
  time_taken: number;
  statistics: AttackStatistics;
  reconstructed_image: string;
  true_image: string;
}