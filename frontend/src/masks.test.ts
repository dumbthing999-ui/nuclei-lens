import {describe,it,expect} from 'vitest';
import {fromArrayBuffer} from 'geotiff';
import {deflateSync} from 'node:zlib';
import {applyMaskProposal,countInstances,undoMaskPatch,labelTiff,decodeLabelMaps} from './masks';
import type {Analysis,GraphEvent} from './types';
const event=(baseline_ids:number[],alternate_ids:number[]):GraphEvent=>({kind:'split alternative',baseline_count:baseline_ids.length,alternate_count:alternate_ids.length,baseline_ids,alternate_ids,run_id:1,bbox:[0,0,4,1],magnitude:1});
describe('explicit graph component mask replacement',()=>{
 const baseline=Uint32Array.of(1,1,2,2,3,3);
 const alternative=Uint32Array.of(1,2,3,3,3,3);
 it('applies opposing real components while the net total stays unchanged',()=>{
  const split=applyMaskProposal(baseline,baseline,alternative,event([1],[1,2]));
  expect(countInstances(split.mask)).toBe(4);
  const merge=applyMaskProposal(split.mask,baseline,alternative,event([2,3],[3]));
  expect(countInstances(merge.mask)).toBe(3);expect(merge.mask).not.toEqual(baseline);
  expect(undoMaskPatch(merge.mask,merge.patch)).toEqual(split.mask);
  expect(undoMaskPatch(split.mask,split.patch)).toEqual(baseline);
  expect(baseline).toEqual(Uint32Array.of(1,1,2,2,3,3));
 });
 it('rejects conflicts, overlapping/repeated edits, missing IDs and inconsistent cardinalities',()=>{
  expect(()=>applyMaskProposal(baseline,baseline,alternative,event([1],[1,3]))).toThrow(/retained/);
  const split=applyMaskProposal(baseline,baseline,alternative,event([1],[1,2]));
  expect(()=>applyMaskProposal(split.mask,baseline,alternative,event([1],[1,2]))).toThrow(/already edited/);
  expect(()=>applyMaskProposal(baseline,baseline,alternative,event([99],[1]))).toThrow();
  expect(()=>applyMaskProposal(baseline,baseline,alternative,{...event([1],[1]),baseline_count:2})).toThrow(/Invalid/);
  expect(()=>applyMaskProposal(baseline,baseline,alternative,event([1,1],[1]))).toThrow(/Invalid/);
  expect(()=>applyMaskProposal(baseline,baseline,alternative,event([0],[1]))).toThrow(/Invalid/);
  expect(()=>applyMaskProposal(baseline,baseline.slice(1),alternative,event([1],[1]))).toThrow(/dimensions/);
 });
 it('rejects uint32 ID exhaustion without modifying the input',()=>{
  const current=Uint32Array.of(4294967295,1),before=current.slice();
  expect(()=>applyMaskProposal(current,current,Uint32Array.of(1,1),event([1,4294967295],[1]))).toThrow(/exhausted/);expect(current).toEqual(before);
 });
 it('requires untouched source geometry and handles explicit loss/addition',()=>{
  const lost=applyMaskProposal(baseline,baseline,alternative,event([1],[]));expect(countInstances(lost.mask)).toBe(2);
  const empty=new Uint32Array(6),added=applyMaskProposal(empty,empty,alternative,event([],[1]));expect(countInstances(added.mask)).toBe(1);
  const modified=baseline.slice();modified[0]=0;expect(()=>applyMaskProposal(modified,baseline,alternative,event([1],[1,2]))).toThrow(/already edited/);
 });
 it('exports lossless unsigned 32-bit TIFF that an independent TIFF parser reads exactly',async()=>{
  const mask=Uint32Array.of(0,1,256,65536,4294967295,3);const bytes=labelTiff(mask,3,2);
  const tiff=await fromArrayBuffer(bytes.buffer as ArrayBuffer),image=await tiff.getImage();
  expect(image.getWidth()).toBe(3);expect(image.getHeight()).toBe(2);
  const decoded=await image.readRasters({interleave:true});
  expect(decoded).toBeInstanceOf(Uint32Array);expect(Array.from(decoded)).toEqual(Array.from(mask));
  expect(()=>labelTiff(mask,4,2)).toThrow();
 });
 it('bounds compressed assets and verifies source run counts',async()=>{
  const data=Buffer.alloc(4*baseline.length);baseline.forEach((id,i)=>data.writeUInt32LE(id,i*4));
  const analysis={width:6,height:1,run_counts:[3],label_maps:{encoding:'zlib-base64-uint32-le',runs:[deflateSync(data).toString('base64')]}} as Analysis;
  expect((await decodeLabelMaps(analysis))[0]).toEqual(baseline);
  await expect(decodeLabelMaps({...analysis,run_counts:[4]})).rejects.toThrow(/reported/);
  await expect(decodeLabelMaps({...analysis,width:1})).rejects.toThrow(/dimensions/);
 });
});
