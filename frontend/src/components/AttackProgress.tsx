import { AttackStatistics } from "./AttackStatistics";

// TypeScript interface for AttackProgress
export interface AttackProgress {
  attack_start_time_s: number;
  current_iteration: number;
  max_iterations: number;
  current_restart: number;
  max_restarts: number;
  current_batch: number;
  max_batches: number;
  time_taken: number;
  statistics: AttackStatistics;
  true_image: string;
  reconstructed_image: string;
  true_text: string;
  reconstructed_text: string;  
}
