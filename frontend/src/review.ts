import type { Analysis, Correction } from './types';

export function reviewedTotal(analysis: Analysis, corrections: Record<number, Correction>): number {
  return analysis.raw_count + Object.values(corrections).reduce((sum, c) => sum + c.reviewed_count - c.baseline_count, 0);
}
export function validateCount(value:string): number {
  if (!/^\d+$/.test(value)) throw new Error('Enter a whole number from 0 to 1,000.');
  const count = Number(value);
  if (!Number.isSafeInteger(count) || count > 1000) throw new Error('Enter a whole number from 0 to 1,000.');
  return count;
}
export function auditDocument(analysis:Analysis, corrections:Record<number,Correction>, filename:string) {
  return {schema_version:1, product:'NucleiLens', software_version:analysis.software_version,
    exported_at:new Date().toISOString(), filename, input_hash:analysis.input_hash, config:analysis.config,
    baseline_count:analysis.raw_count, reviewed_count:reviewedTotal(analysis, corrections),
    sensitivity_range:analysis.sensitivity_range, corrections:Object.values(corrections),
    mask_modifications:false, limitations:analysis.limitations,
    review_semantics:'Counts refer to baseline-object centroids within fixed tiles. Reviewed counts are human entries, not validated ground truth.'};
}

export function compatibleReview(previous:Analysis|null, next:Analysis, corrections:Record<number,Correction>): Record<number,Correction> {
  if (!previous || previous.input_hash !== next.input_hash || JSON.stringify(previous.config) !== JSON.stringify(next.config)) return {};
  return Object.fromEntries(Object.entries(corrections).filter(([, correction]) =>
    next.regions.some(region => region.id === correction.region_id && region.baseline_count === correction.baseline_count)));
}
export function cancellationWitness(analysis:Analysis) {
  for (let run = 1; run < analysis.run_counts.length; run++) {
    if (analysis.run_counts[run] !== analysis.raw_count) continue;
    const events = analysis.regions.flatMap(region => region.events.filter(event => event.run_id === run).map(event => ({region_id:region.id, ...event})));
    const split = events.find(event => event.kind === 'split alternative');
    const merge = events.find(event => event.kind === 'merge alternative');
    if (split && merge) return {run, split, merge};
  }
  return null;
}
