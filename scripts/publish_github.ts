import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
const git=(...args)=>execFileSync('git',args,{encoding:'utf8'}).trim();
const f=await proxy('github');const base='https://api.github.com/repos/dumbthing999-ui/nuclei-lens';
async function call(path,method='GET',body=undefined){const r=await f(base+path,{method,headers:{'Content-Type':'application/json'},...(body?{body}:{})});const d=await r.json();if(!r.ok)throw new Error(JSON.stringify({path,status:r.status,message:d.message}));return d;}
const local=git('rev-parse','HEAD');const parent=git('rev-parse','HEAD^');const expectedTree=git('rev-parse','HEAD^{tree}');
const branch=git('branch','--show-current');if(!branch)throw new Error('Publish a named branch, not detached HEAD.');
const probe=await f(base+'/git/ref/heads/'+branch);let exists=probe.status===200;if(!exists&&probe.status!==404)throw new Error('Cannot read branch state '+probe.status);const current=exists?await probe.json():await call('/git/ref/heads/main');if(current.object.sha===local){console.log('Source already published '+local);process.exit(0);}if(current.object.sha!==parent)throw new Error('Remote advanced; preserve history and reconcile before retry.');
const cachePath='.firecrawl/github-blob-cache.json';const cache=existsSync(cachePath)?JSON.parse(readFileSync(cachePath,'utf8')):{};
const entries=execFileSync('git',['ls-files','-s','-z'],{encoding:'utf8'}).split('\0').filter(Boolean);const tree=[];
for(const entry of entries){const [info,path]=entry.split('\t');const [mode,blobSha]=info.split(' ');const bytes=execFileSync('git',['show',`HEAD:${path}`],{maxBuffer:20000000});const text=bytes.toString('utf8');
 if(bytes.length<32000&&!text.includes('\0')&&Buffer.from(text).equals(bytes)){tree.push({path,mode,type:'blob',content:text});}
 else{if(!cache[blobSha]){const blob=await call('/git/blobs','POST',{content:bytes.toString('base64'),encoding:'base64'});if(blob.sha!==blobSha)throw new Error('Blob hash mismatch');cache[blobSha]=blob.sha;writeFileSync(cachePath,JSON.stringify(cache));console.log('Uploaded exact blob '+path);}tree.push({path,mode,type:'blob',sha:cache[blobSha]});}}
const createdTree=await call('/git/trees','POST',{tree});if(createdTree.sha!==expectedTree)throw new Error('Exact local/remote tree mismatch; ref not moved.');
const fields=git('show','-s','--format=%an%n%ae%n%aI%n%cn%n%ce%n%cI%n%B','HEAD').split('\n');const [an,ae,ad,cn,ce,cd,...message]=fields;
const commit=await call('/git/commits','POST',{message:message.join('\n'),tree:createdTree.sha,parents:[parent],author:{name:an,email:ae,date:ad},committer:{name:cn,email:ce,date:cd}});
if(commit.tree.sha!==expectedTree||commit.parents[0].sha!==parent||Date.parse(commit.author.date)!==Date.parse(ad)||Date.parse(commit.committer.date)!==Date.parse(cd))throw new Error('Commit provenance mismatch; ref preserved.');
if(exists)await call('/git/refs/heads/'+branch,'PATCH',{sha:commit.sha,force:false});else await call('/git/refs','POST',{ref:'refs/heads/'+branch,sha:commit.sha});const verify=await call('/git/ref/heads/'+branch);if(verify.object.sha!==commit.sha)throw new Error('Readback mismatch');
writeFileSync('evaluation/checks/github-publication.json',JSON.stringify({generated_at:new Date().toISOString(),repository:'https://github.com/dumbthing999-ui/nuclei-lens',branch,commit_sha:commit.sha,local_commit_sha:local,tree_sha:expectedTree,files:tree.length,readback_verified:true},null,2)+'\n');
console.log(JSON.stringify({branch,published_commit:commit.sha,local_commit:local,files:tree.length,readback_verified:true}));
