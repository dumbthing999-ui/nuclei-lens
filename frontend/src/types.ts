export interface GraphEvent {
  kind:string;baseline_count:number;alternate_count:number;run_id:number;
  magnitude:number;bbox:number[];baseline_ids:number[];alternate_ids:number[];
}
export interface Region {
  id: number; bbox: [number, number, number, number]; baseline_count: number;
  run_counts: number[]; candidate_counts: number[]; score: number; reasons: string[];
  events: GraphEvent[];
  comparators: Record<string, number>;
}
export interface Analysis {
  schema_version:number;software_version:string;input_hash:string;width:number;height:number;
  raw_count:number;sensitivity_range:[number,number];run_counts:number[];run_names:string[];
  config:Record<string,number>;regions:Region[];flagged_regions:number;analysis_ms:number;
  quality?:{signal_to_noise_heuristic:number;weak_signal:boolean;warning:string|null};
  image_png:string;outline_pngs:string[];boundary_png:string;limitations:string[];
  label_maps?:{encoding:'zlib-base64-uint32-le';runs:string[]};
}
export interface Sample { id:string;title:string;filename:string;note:string;analysis_url:string;image_url:string;reference_count:number;f1:number; }
export interface Correction { region_id:number;baseline_count:number;reviewed_count:number;note:string;at:string; }

export interface Benchmark { split:string;n_images:number;count_mae:number;mean_f1:number;methods:Record<string,{capture_at_20_percent:number;capture_ci95:number[]}>; }
