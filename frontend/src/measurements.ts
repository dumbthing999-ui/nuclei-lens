/** Pixel geometry only: no intensity, physical calibration, or biological truth. */
export interface LabelMeasurement {
  label: number;
  area_px: number;
  centroid_x_px: number;
  centroid_y_px: number;
  grid_edge_perimeter_px: number;
  bbox_xyxy: [number, number, number, number];
  touches_image_border: boolean;
}
export interface MaskMeasurements {
  object_count: number;
  foreground_pixels: number;
  mean_area_px: number | null;
  median_area_px: number | null;
  objects: LabelMeasurement[];
}
export function measureMask(mask: Uint32Array, width: number, height: number): MaskMeasurements {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1 ||
      width * height !== mask.length || mask.length > 1048576) throw new Error('Invalid mask dimensions.');
  const rows = new Map<number, {area:number;x:number;y:number;perimeter:number;bbox:[number,number,number,number];border:boolean}>();
  let foreground = 0;
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const index = y * width + x, label = mask[index];
    if (!label) continue;
    let row = rows.get(label);
    if (!row) {
      if (rows.size >= 10000) throw new Error('Mask exceeds 10,000 instances. Use a smaller field.');
      row = {area:0,x:0,y:0,perimeter:0,bbox:[x,y,x+1,y+1],border:false}; rows.set(label, row);
    }
    foreground++; row.area++; row.x += x + 0.5; row.y += y + 0.5;
    row.bbox = [Math.min(row.bbox[0],x),Math.min(row.bbox[1],y),Math.max(row.bbox[2],x+1),Math.max(row.bbox[3],y+1)];
    row.border ||= x === 0 || y === 0 || x === width - 1 || y === height - 1;
    row.perimeter += Number(x === 0 || mask[index-1] !== label) + Number(x === width-1 || mask[index+1] !== label) +
      Number(y === 0 || mask[index-width] !== label) + Number(y === height-1 || mask[index+width] !== label);
  }
  const objects = [...rows.entries()].sort(([a],[b])=>a-b).map(([label,row])=>({
    label, area_px:row.area, centroid_x_px:row.x/row.area, centroid_y_px:row.y/row.area,
    grid_edge_perimeter_px:row.perimeter, bbox_xyxy:row.bbox, touches_image_border:row.border,
  }));
  const areas = objects.map(row=>row.area_px).sort((a,b)=>a-b), middle = Math.floor(areas.length/2);
  return {object_count:objects.length,foreground_pixels:foreground,mean_area_px:objects.length?foreground/objects.length:null,
    median_area_px:areas.length?(areas.length%2?areas[middle]:(areas[middle-1]+areas[middle])/2):null,objects};
}
export function measurementsCsv(measurements: MaskMeasurements, hash: string): string {
  if (!/^[0-9a-f]{64}$/.test(hash)) throw new Error('A verified mask hash is required.');
  const header = 'mask_sha256_uint32_le,label,area_px,centroid_x_px,centroid_y_px,grid_edge_perimeter_px,bbox_min_x,bbox_min_y,bbox_max_x_exclusive,bbox_max_y_exclusive,touches_image_border';
  return [header,...measurements.objects.map(row=>[hash,row.label,row.area_px,row.centroid_x_px,row.centroid_y_px,
    row.grid_edge_perimeter_px,...row.bbox_xyxy,Number(row.touches_image_border)].join(','))].join('\n')+'\n';
}
