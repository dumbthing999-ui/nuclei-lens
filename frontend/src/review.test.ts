import { describe, expect, it } from 'vitest';
import { validateCount, reviewedTotal, auditDocument, compatibleReview, cancellationWitness } from './review';
import type { Analysis, Correction } from './types';

describe('auditable review', () => {
  it('validates bounded integer counts', () => {
    expect(validateCount('0')).toBe(0); expect(validateCount('1000')).toBe(1000);
    for (const value of ['-1','1.5','1001','NaN','']) expect(() => validateCount(value)).toThrow();
  });
  it('applies local differences and never implies changed masks', () => {
    const analysis = {raw_count:20,software_version:'0.1.0',input_hash:'hash',config:{},sensitivity_range:[18,22],limitations:[]} as unknown as Analysis;
    const corrections:Record<number,Correction> = {1:{region_id:1,baseline_count:5,reviewed_count:4,note:'split',at:'now'},2:{region_id:2,baseline_count:3,reviewed_count:4,note:'merge',at:'now'}};
    expect(reviewedTotal(analysis, corrections)).toBe(20);
    expect(auditDocument(analysis,corrections,'sample.tif').mask_modifications).toBe(false);
    delete corrections[2]; expect(reviewedTotal(analysis,corrections)).toBe(19);
  });
});


describe('repeatable inspection', () => {
  const analysis = {input_hash:'same',config:{threshold:0.85},raw_count:3,run_counts:[3,3],regions:[{id:0,baseline_count:3,events:[{kind:'split alternative',run_id:1,baseline_count:1,alternate_count:2},{kind:'merge alternative',run_id:1,baseline_count:2,alternate_count:1}]}]} as unknown as Analysis;
  const corrections = {0:{region_id:0,baseline_count:3,reviewed_count:4,note:'manual',at:'now'}};
  it('retains compatible reviews only for the same data, config, and region baseline', () => {
    expect(compatibleReview(analysis,analysis,corrections)).toEqual(corrections);
    expect(compatibleReview(analysis,{...analysis,input_hash:'other'},corrections)).toEqual({});
    expect(compatibleReview(analysis,{...analysis,config:{threshold:0.9}},corrections)).toEqual({});
    expect(compatibleReview(analysis,{...analysis,regions:[{...analysis.regions[0],baseline_count:2}]},corrections)).toEqual({});
  });
  it('requires equal measured totals and opposing graph events for the signature example', () => {
    expect(cancellationWitness(analysis)?.run).toBe(1);
    expect(cancellationWitness({...analysis,run_counts:[3,4]})).toBeNull();
    expect(cancellationWitness({...analysis,regions:[{...analysis.regions[0],events:analysis.regions[0].events.slice(0,1)}]})).toBeNull();
  });
});
