/* Dedicated worker: image bytes never leave this browser. */
import {fromArrayBuffer} from 'geotiff';
let pyodide;
let busy = false;
async function boot() {
  if (pyodide) return pyodide;
  postMessage({type:'status', status:'Loading the local analysis engine…'});
  const runtimeUrl='/runtime/pyodide/pyodide.mjs';
  const {loadPyodide}=await import(/* @vite-ignore */ runtimeUrl);
  pyodide = await loadPyodide({indexURL:'/runtime/pyodide/'});
  postMessage({type:'status', status:'Loading microscopy libraries…'});
  await pyodide.loadPackage(['numpy','scipy','scikit-image']);
  pyodide.FS.mkdirTree('/home/pyodide/nuclei_lens');
  for (const name of ['__init__.py','core.py','graph.py','raster.py']) {
    const response = await fetch('/engine/nuclei_lens/' + name);
    if (!response.ok) throw new Error('Analysis source could not be loaded.');
    pyodide.FS.writeFile('/home/pyodide/nuclei_lens/' + name, await response.text());
  }
  await pyodide.runPythonAsync('import json\nimport numpy as np\nfrom nuclei_lens.core import analyze\nfrom nuclei_lens.raster import serialize');
  postMessage({type:'ready'});
  return pyodide;
}
onmessage = async ({data}) => {
  if (busy) return;
  busy = true;
  try {
    await boot();
    if (data.type === 'analyze') {
      const decoded=await decodeRaster(data.buffer);
      postMessage({type:'status',status:'Comparing nine segmentations on your device…'});
      pyodide.globals.set('input_bytes',new Uint8Array(decoded.pixels.buffer,decoded.pixels.byteOffset,decoded.pixels.byteLength));
      pyodide.globals.set('input_dtype',decoded.dtype);
      pyodide.globals.set('input_width',decoded.width);
      pyodide.globals.set('input_height',decoded.height);
      const text = await pyodide.runPythonAsync('json.dumps(serialize(analyze(np.frombuffer(bytes(input_bytes.to_py()), dtype=input_dtype).reshape(input_height, input_width))))');
      for(const name of ['input_bytes','input_dtype','input_width','input_height']) pyodide.globals.delete(name);
      postMessage({type:'result', result:JSON.parse(text)});
    }
  } catch(error) {
    postMessage({type:'error',error:error instanceof Error ? error.message : String(error)});
  } finally { busy = false; }
};

function validateDimensions(width,height) {
  if(width<32||height<32||width>2048||height>2048||width*height>1048576) throw new Error('Use a field at least 32 × 32 pixels, at most 1,048,576 pixels and 2,048 pixels per side.');
}
async function decodeRaster(buffer) {
  if(!buffer.byteLength||buffer.byteLength>10*1024*1024) throw new Error('Use a file smaller than 10 MB.');
  const data=new Uint8Array(buffer),view=new DataView(buffer);
  if(data.length>=4&&((data[0]===73&&data[1]===73)||(data[0]===77&&data[1]===77))) {
    const tiff=await fromArrayBuffer(buffer);
    if(await tiff.getImageCount()!==1)throw new Error('Use a single-field TIFF, not a stack.');
    const image=await tiff.getImage();const width=image.getWidth(),height=image.getHeight();validateDimensions(width,height);
    if(image.getSamplesPerPixel()!==1)throw new Error('Use a single-channel nucleus-stained TIFF.');
    const pixels=await image.readRasters({interleave:true});
    const types={Uint8Array:'uint8',Uint16Array:'uint16',Uint32Array:'uint32',Int8Array:'int8',Int16Array:'int16',Int32Array:'int32',Float32Array:'float32',Float64Array:'float64'};
    const dtype=types[pixels.constructor.name];if(!dtype)throw new Error('Unsupported TIFF pixel type.');
    return {pixels,dtype,width,height};
  }
  let width,height;
  if(data.length>=24&&data[0]===137&&data[1]===80&&data[2]===78&&data[3]===71) {
    width=view.getUint32(16);height=view.getUint32(20);
  } else if(data.length>=4&&data[0]===255&&data[1]===216) {
    let offset=2;
    while(offset+4<data.length) {
      if(data[offset++]!==255)throw new Error('Malformed JPEG.');
      while(data[offset]===255)offset++;
      const marker=data[offset++];
      if(marker===217||marker===218)break;
      if(marker===1||(marker>=208&&marker<=215))continue;
      if(offset+2>data.length)break;
      const length=view.getUint16(offset);
      if(length<2||offset+length>data.length)throw new Error('Malformed JPEG metadata.');
      if([192,193,194,195,197,198,199,201,202,203,205,206,207].includes(marker)) {
        if(length<7)throw new Error('Malformed JPEG dimensions.');
        height=view.getUint16(offset+3);width=view.getUint16(offset+5);break;
      }
      offset+=length;
    }
  }
  if(!width||!height)throw new Error('Supported formats are PNG, JPEG, or single-channel TIFF.');
  validateDimensions(width,height);
  const bitmap=await createImageBitmap(new Blob([buffer]));
  if(bitmap.width!==width||bitmap.height!==height){bitmap.close();throw new Error('Image dimensions are inconsistent.');}
  const canvas=new OffscreenCanvas(width,height),context=canvas.getContext('2d');
  context.drawImage(bitmap,0,0);bitmap.close();
  const rgba=context.getImageData(0,0,width,height).data,pixels=new Uint8Array(width*height);
  for(let i=0;i<pixels.length;i++)pixels[i]=Math.round(.299*rgba[i*4]+.587*rgba[i*4+1]+.114*rgba[i*4+2]);
  return {pixels,dtype:'uint8',width,height};
}
