import {afterEach,describe,it,expect,vi} from 'vitest';
import {loadModelExamples,MODEL_EXAMPLE_INPUT_HASH} from './modelExamples';

afterEach(()=>vi.unstubAllGlobals());
describe('bundled neural prediction integrity',()=>{
  it('does not fetch predictions for a different field or geometry',async()=>{
    const fetcher=vi.fn();vi.stubGlobal('fetch',fetcher);
    await expect(loadModelExamples('different',696,520)).rejects.toThrow(/only/);
    await expect(loadModelExamples(MODEL_EXAMPLE_INPUT_HASH,695,520)).rejects.toThrow(/only/);
    expect(fetcher).not.toHaveBeenCalled();
  });
  it('reports missing static assets without supplying predictions',async()=>{
    vi.stubGlobal('fetch',vi.fn(async()=>new Response('',{status:503})));
    await expect(loadModelExamples(MODEL_EXAMPLE_INPUT_HASH,696,520)).rejects.toThrow(/could not be loaded/);
  });
  it('rejects changed file bytes before TIFF parsing',async()=>{
    vi.stubGlobal('fetch',vi.fn(async()=>new Response(new Uint8Array([1,2,3]))));
    await expect(loadModelExamples(MODEL_EXAMPLE_INPUT_HASH,696,520)).rejects.toThrow(/integrity/);
  });
});
