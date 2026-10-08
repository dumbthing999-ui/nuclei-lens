import {describe,it,expect} from 'vitest';
import {readLabelTiff} from './labelImport';
import {labelTiff} from './masks';

describe('strict external label TIFF import',()=>{
  const labels=Uint32Array.of(0,1,65536,4294967295);
  const data=()=>labelTiff(labels,2,2).buffer;
  function changeTag(tag:number,value:number) {
    const bytes=data(),v=new DataView(bytes);
    for(let offset=10;offset<130;offset+=12)if(v.getUint16(offset,true)===tag){v.setUint32(offset+8,value,true);break;}
    return bytes;
  }
  it('reads uint32 IDs exactly with zero background and no resampling',async()=>{
    expect(await readLabelTiff(data(),2,2)).toEqual(labels);
    await expect(readLabelTiff(data(),4,1)).rejects.toThrow(/dimensions/);
  });
  it('rejects signed/float/color layouts and keeps legal overlong strip hints bounded',async()=>{
    await expect(readLabelTiff(changeTag(339,2),2,2)).rejects.toThrow(/unsigned/);
    await expect(readLabelTiff(changeTag(339,3),2,2)).rejects.toThrow(/unsigned/);
    await expect(readLabelTiff(changeTag(277,3),2,2)).rejects.toThrow(/single-channel/);
    await expect(readLabelTiff(changeTag(259,8),2,2)).rejects.toThrow(/uncompressed/);
    // GeoTIFF clamps the effective final strip to image height before allocation.
    await expect(readLabelTiff(changeTag(278,4294967295),2,2)).resolves.toEqual(labels);
  });
  it('rejects invalid and oversized inputs before raster allocation',async()=>{
    await expect(readLabelTiff(new ArrayBuffer(4),2,2)).rejects.toThrow(/10 MB/);
    await expect(readLabelTiff(new ArrayBuffer(10*1024*1024+1),2,2)).rejects.toThrow(/10 MB/);
    await expect(readLabelTiff(new ArrayBuffer(16),2,2)).rejects.toThrow();
  });
});
