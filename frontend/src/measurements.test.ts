import {describe,it,expect} from 'vitest';
import {measureMask,measurementsCsv} from './measurements';
import {applyMaskProposal,undoMaskPatch} from './masks';
import {compareMasks} from './maskComparison';

describe('pixel measurements and sparse model correspondence',()=>{
  it('measures exact area, pixel-center centroid, exposed edges and exclusive bounding box',()=>{
    const m=measureMask(Uint32Array.of(0,0,0,0,9,0,0,0,0),3,3);
    expect(m.objects).toEqual([{label:9,area_px:1,centroid_x_px:1.5,centroid_y_px:1.5,
      grid_edge_perimeter_px:4,bbox_xyxy:[1,1,2,2],touches_image_border:false}]);
    expect(m.mean_area_px).toBe(1);expect(m.median_area_px).toBe(1);
  });
  it('handles uint32 IDs, disconnected same-ID pixels, border and empty fields explicitly',()=>{
    const m=measureMask(Uint32Array.of(4294967295,0,4294967295,2),2,2);
    expect(m.objects.map(row=>row.label)).toEqual([2,4294967295]);
    expect(m.objects[1]).toMatchObject({area_px:2,centroid_x_px:0.5,centroid_y_px:1,grid_edge_perimeter_px:6,touches_image_border:true});
    expect(measureMask(new Uint32Array(4),2,2)).toMatchObject({object_count:0,mean_area_px:null,median_area_px:null});
    expect(()=>measureMask(new Uint32Array(4),3,2)).toThrow(/dimensions/);
    expect(()=>measureMask(Uint32Array.from({length:10001},(_,i)=>i+1),10001,1)).toThrow(/10,000/);
  });
  it('does not confuse harmless ID renumbering with segmentation disagreement',()=>{
    const m=compareMasks(Uint32Array.of(1,1,2,2),Uint32Array.of(90,90,40,40),4,1);
    expect(m).toMatchObject({same_total:true,segmentation_equal_up_to_ids:true,label_value_difference_pixels:4,foreground_difference_pixels:0,events:[]});
  });
  it('finds opposing split/merge components even when counts and foreground areas match',()=>{
    const baseline=Uint32Array.of(1,1,2,2,3,3),alt=Uint32Array.of(1,2,3,3,3,3);
    const m=compareMasks(baseline,alt,6,1);
    expect(m).toMatchObject({same_total:true,segmentation_equal_up_to_ids:false,foreground_difference_pixels:0,overlap_min_area_threshold:0.45});
    expect(m.events.map(e=>e.kind)).toEqual(['split alternative','merge alternative']);
    const first=applyMaskProposal(baseline,baseline,alt,m.events[0]),second=applyMaskProposal(first.mask,baseline,alt,m.events[1]);
    expect(measureMask(first.mask,6,1)).toMatchObject({object_count:4,mean_area_px:1.5});
    expect(measureMask(second.mask,6,1)).toMatchObject({object_count:3,mean_area_px:2});
    expect(measureMask(second.mask,6,1).objects.map(x=>x.area_px).sort()).toEqual([1,1,4]);
    const restored=undoMaskPatch(undoMaskPatch(second.mask,second.patch),first.patch);
    expect(measureMask(restored,6,1)).toEqual(measureMask(baseline,6,1));
  });
  it('retains boundary, missing and appearing objects as hypotheses without ground truth',()=>{
    const boundary=compareMasks(Uint32Array.of(1,1,0),Uint32Array.of(5,0,0),3,1);
    expect(boundary.events[0].kind).toBe('boundary alternative');expect(boundary.foreground_difference_pixels).toBe(1);
    const disjoint=compareMasks(Uint32Array.of(1,0),Uint32Array.of(0,9),2,1);
    expect(disjoint.events.map(x=>x.kind)).toEqual(['loss alternative','addition alternative']);
    expect(disjoint.same_total).toBe(true);expect(disjoint.segmentation_equal_up_to_ids).toBe(false);
    expect(compareMasks(new Uint32Array(2),new Uint32Array(2),2,1).segmentation_equal_up_to_ids).toBe(true);
  });
  it('exports numeric measurements with the supplied verified-mask hash',()=>{
    const hash='a'.repeat(64),m=measureMask(Uint32Array.of(1,1),2,1),csv=measurementsCsv(m,hash);
    expect(csv.split('\n')[1]).toBe(`${hash},1,2,1,0.5,6,0,0,2,1,1`);
    expect(()=>measurementsCsv(m,'=formula')).toThrow(/hash/);
  });
});
