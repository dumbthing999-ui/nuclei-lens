import {fromArrayBuffer} from 'geotiff';

export async function readLabelTiff(bytes: ArrayBuffer, width: number, height: number): Promise<Uint32Array> {
  if(bytes.byteLength<8||bytes.byteLength>10*1024*1024) throw new Error('Use a label TIFF smaller than 10 MB.');
  const tiff=await fromArrayBuffer(bytes);
  const image=await tiff.getImage(), directory=image.getFileDirectory();
  if(directory.nextIFDByteOffset!==0) throw new Error('Use one 2D label image, not a multi-page stack.');
  if(image.getWidth()!==width||image.getHeight()!==height||width*height>1048576) throw new Error('Label TIFF dimensions must exactly match this field. No resampling is performed.');
  if(image.getSamplesPerPixel()!==1||![8,16,32].includes(image.getBitsPerSample())||image.getSampleFormat()!==1) throw new Error('Use single-channel unsigned 8-, 16-, or 32-bit instance IDs, with zero as background.');
  if((directory.getValue('Compression')??1)!==1) throw new Error('Export an uncompressed label TIFF (compression=none) before comparison.');
  const tileWidth=image.getTileWidth(),tileHeight=image.getTileHeight();
  if(!Number.isFinite(tileWidth)||!Number.isFinite(tileHeight)||tileWidth<1||tileHeight<1||tileWidth*tileHeight>1048576) throw new Error('TIFF tile or strip dimensions exceed the supported bound.');
  if((directory.getValue('PlanarConfiguration')??1)!==1) throw new Error('Unsupported TIFF channel layout.');
  if((await directory.loadValue('Orientation')??1)!==1) throw new Error('Export label TIFF in top-left orientation before comparison.');
  const raster=await image.readRasters({interleave:true});
  if(!(raster instanceof Uint8Array||raster instanceof Uint16Array||raster instanceof Uint32Array)||raster.length!==width*height) throw new Error('TIFF did not decode to an unsigned instance-label map.');
  return Uint32Array.from(raster);
}
