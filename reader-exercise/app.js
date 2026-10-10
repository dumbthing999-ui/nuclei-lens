'use strict';

(() => {
  const $ = id => document.getElementById(id);
  const synthetic = new URLSearchParams(location.search).get('test') === '1';
  $('synthetic').hidden = !synthetic;
  const state = {manifest: null, contract: null, participant: null, experience: null,
    retention: null, consent: false, assignments: [], records: [], index: -1,
    practice: true, practiceDone: false, asset: null, draft: null, started: false,
    ended: false, stopped: false, loading: false, selectedTile: null, fullField: false,
    startMono: null, timer: null, assetDigest: null, sealed: false};
  const integer = (value, low, high) => Number.isInteger(value) && value >= low && value <= high;
  const require = (condition, message) => {if (!condition) throw new Error(message);};
  const showError = error => {$('error').textContent = String(error.message || error); $('error').hidden = false;};
  const clearError = () => {$('error').hidden = true; $('error').textContent = '';};
  const canonical = value => Array.isArray(value) ? `[${value.map(canonical).join(',')}]` :
    value && typeof value === 'object' ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}` : JSON.stringify(value);
  const sha256 = async bytes => {
    require(globalThis.crypto?.subtle, 'SHA-256 requires a trustworthy local context. Serve on loopback.');
    return [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(byte => byte.toString(16).padStart(2, '0')).join('');
  };
  const text = (tag, content, className) => {
    const element = document.createElement(tag); element.textContent = content;
    if (className) element.className = className;
    return element;
  };
  function publicHash(name) {
    const manifest = state.manifest;
    const maps = [manifest?.asset_sha256, manifest?.asset_hashes, manifest?.served_files, manifest?.seal?.served_files];
    const supplied = maps.filter(map => map && Object.hasOwn(map, name)).map(map =>
      typeof map[name] === 'string' ? map[name] : map[name]?.sha256);
    if (!supplied.length) return null;
    require(supplied.every(hash => typeof hash === 'string' && /^[a-f0-9]{64}$/.test(hash)) &&
      new Set(supplied).size === 1, `Invalid public seal for ${name}`);
    return supplied[0];
  }
  async function loadJSON(name) {
    require(/^(manifest|export-contract|Q01-B|F0[1-4]-[AB])\.json$/.test(name), 'Unapproved asset path');
    const response = await fetch(new URL(name, location.href), {cache: 'no-store', credentials: 'omit', signal: AbortSignal.timeout(20000)});
    require(response.ok, `Local asset unavailable: ${name} (${response.status})`);
    require(new URL(response.url).origin === location.origin, 'Asset redirected to another origin');
    const bytes = await response.arrayBuffer(), actualHash = await sha256(bytes), expected = publicHash(name);
    require(!expected || actualHash === expected, `SHA-256 mismatch: ${name}`);
    return {data: JSON.parse(new TextDecoder().decode(bytes)), actualHash, sealed: !!expected};
  }
  const assignmentKeys = ['task_id', 'order', 'field_id', 'arm_id', 'tile_ids', 'input_hash', 'field_hash', 'config_hash', 'assignment_hash'];
  const exportKeys = ['schema_version', 'protocol_hash', 'participant_id', 'synthetic_test', 'experience_band', 'retention_choice', 'consent_acknowledged', 'tasks'];
  const taskKeys = [...assignmentKeys, 'started_at', 'ended_at', 'elapsed_ms', 'visibility_interruptions_ms', 'status', 'reason', 'regions', 'comprehension'];
  const regionKeys = ['tile_id', 'baseline_count', 'entered_count', 'uncertainty', 'confirmed', 'status', 'reason'];
  const sameKeys = (actual, expected) => Array.isArray(actual) && canonical([...actual].sort()) === canonical([...expected].sort());
  async function validateManifest(manifest, contract) {
    require(manifest.schema_version === 1 && /^[a-f0-9]{64}$/.test(manifest.protocol_hash), 'Unsupported manifest');
    require(contract.schema_version === 1 && sameKeys(contract.required_export_keys, exportKeys) &&
      sameKeys(contract.required_task_keys, taskKeys) && sameKeys(contract.required_region_keys, regionKeys), 'Unsupported export contract');
    require(sameKeys(contract.task_status, ['completed', 'aborted', 'failed']) &&
      sameKeys(contract.region_status, ['completed', 'unresolved', 'not_started']) &&
      canonical(contract.bounds.count) === '[0,1000]' && canonical(contract.bounds.uncertainty) === '[0,3]' &&
      canonical(contract.bounds.elapsed_ms) === '[0,86400000]' && contract.bounds.text_max_length === 500,
    'Unsupported record bounds or statuses');
    require(manifest.practice_id === 'Q01', 'Common practice must be Q01');
    require(sameKeys(Object.keys(manifest.assignments || {}), ['P01', 'P02', 'P03', 'P04', 'P05', 'P06']), 'Expected P01–P06 allocations');
    for (const tasks of Object.values(manifest.assignments)) {
      require(Array.isArray(tasks) && tasks.length === 4 && new Set(tasks.map(task => task.field_id)).size === 4, 'Four distinct assessment fields required');
      for (const [index, assignment] of tasks.entries()) {
        require(sameKeys(Object.keys(assignment), assignmentKeys) && assignment.order === index + 1 &&
          assignment.task_id === `T0${index + 1}` && /^F0[1-4]$/.test(assignment.field_id) &&
          ['A', 'B'].includes(assignment.arm_id), 'Invalid assessment assignment; familiar demo fields are excluded');
        require(Array.isArray(assignment.tile_ids) && assignment.tile_ids.length === 4 &&
          new Set(assignment.tile_ids).size === 4 && assignment.tile_ids.every(tile => integer(tile, 0, 19)), 'Exactly four distinct assigned tiles required');
        require(['input_hash', 'field_hash', 'config_hash', 'assignment_hash'].every(key => /^[a-f0-9]{64}$/.test(assignment[key])), 'Missing assignment hashes');
        require(assignment.config_hash === manifest.config_hash, 'Configuration mismatch');
        const payload = Object.fromEntries(Object.entries(assignment).filter(([key]) => key !== 'assignment_hash'));
        require(await sha256(new TextEncoder().encode(canonical(payload))) === assignment.assignment_hash, 'Assignment hash mismatch');
      }
    }
  }
  function validateAsset(asset, assignment) {
    const common = ['field_id', 'arm_id', 'input_hash', 'field_hash', 'config_hash', 'width', 'height', 'image_png', 'baseline_outline_png', 'regions'];
    require(sameKeys(Object.keys(asset), asset.arm_id === 'B' ? [...common, 'alternative_outline_pngs'] : common), 'Asset contains unexpected data');
    require(asset.field_id === assignment.field_id && asset.arm_id === assignment.arm_id, 'Wrong field or view asset');
    require(asset.config_hash === state.manifest.config_hash, 'Asset configuration mismatch');
    for (const key of ['input_hash', 'field_hash', 'config_hash']) {
      require(/^[a-f0-9]{64}$/.test(asset[key]) && (!assignment[key] || assignment[key] === asset[key]), `Asset identity mismatch: ${key}`);
    }
    require(integer(asset.width, 1, 4096) && integer(asset.height, 1, 4096), 'Unsupported image dimensions');
    require(Array.isArray(asset.regions) && asset.regions.length === 20 &&
      new Set(asset.regions.map(region => region.id)).size === 20, 'Expected twenty fixed tiles');
    for (const region of asset.regions) {
      require(sameKeys(Object.keys(region), asset.arm_id === 'B' ? ['id', 'bbox', 'baseline_count', 'events', 'run_counts'] : ['id', 'bbox', 'baseline_count']), 'Unexpected region data');
      require(integer(region.id, 0, 19) && integer(region.baseline_count, 0, 1000), 'Invalid tile baseline');
      const box = region.bbox;
      require(Array.isArray(box) && box.length === 4 && box.every(Number.isFinite) &&
        box[0] >= 0 && box[1] >= 0 && box[2] <= asset.width && box[3] <= asset.height &&
        box[2] > box[0] && box[3] > box[1], 'Invalid tile bounds');
      if (asset.arm_id === 'B') {
        require(Array.isArray(region.run_counts) && region.run_counts.length === 9 &&
          region.run_counts.every(count => integer(count, 0, 1000)) && Array.isArray(region.events), 'Invalid alternative tile data');
        require(region.events.every(event => integer(event.run_id, 1, 8) &&
          typeof event.kind === 'string' && integer(event.baseline_count, 0, 1000) && integer(event.alternate_count, 0, 1000)), 'Invalid alternative event');
      }
    }
    if (asset.arm_id === 'B') require(Array.isArray(asset.alternative_outline_pngs) && asset.alternative_outline_pngs.length === 8, 'Eight actual alternatives required');
  }
  async function decodePNG(base64, asset) {
    require(typeof base64 === 'string' && base64.startsWith('iVBORw0KGgo') && /^[A-Za-z0-9+/=]+$/.test(base64), 'Expected inline PNG asset');
    const image = new Image(); image.src = `data:image/png;base64,${base64}`;
    await image.decode();
    require(image.naturalWidth === asset.width && image.naturalHeight === asset.height, 'Outline/image dimensions disagree');
  }
  function assignment() {
    return state.practice ? {field_id: 'Q01', arm_id: 'B', tile_ids: [0, 1, 2, 3]} : state.assignments[state.index];
  }
  function elapsed() {
    require(state.startMono !== null, 'Task has not started');
    const value = Math.floor(performance.now() - state.startMono);
    require(integer(value, 0, 86400000), 'Timing exceeds the supported 24-hour record bound; do not invent a duration');
    return value;
  }
  function updateTaskState() {
    if (state.started && !state.ended) {
      try {$('task-state').textContent = `${state.practice ? 'Practice' : 'Task'} running · ${(elapsed() / 1000).toFixed(1)} seconds elapsed · timing continues while hidden.`;}
      catch (error) {clearInterval(state.timer); showError(error);}
    }
  }
  async function loadTask() {
    clearError(); state.loading = true; state.asset = null; state.started = false; state.ended = false;
    state.startMono = null; clearInterval(state.timer); state.fullField = false;
    $('exercise').hidden = true; $('next').hidden = true;
    $('task-state').textContent = 'Loading and validating all field and outline assets. Timing has not started.';
    const task = assignment();
    $('session-title').textContent = state.practice ? 'Common practice · View B' : `Task ${task.order} of 4 · View ${task.arm_id}`;
    $('progress').textContent = `${state.participant} · ${state.records.length} assessment tasks saved in memory. Practice is not exported.`;
    try {
      const loaded = await loadJSON(`${task.field_id}-${task.arm_id}.json`);
      validateAsset(loaded.data, task);
      const asset = loaded.data;
      await Promise.all([asset.image_png, asset.baseline_outline_png, ...(asset.alternative_outline_pngs || [])].map(png => decodePNG(png, asset)));
      if (state.stopped) return;
      state.asset = asset; state.assetDigest = loaded.actualHash; state.sealed = loaded.sealed;
      state.selectedTile = task.tile_ids[0];
      state.draft = {...task, started_at: null, ended_at: null, elapsed_ms: null,
        visibility_interruptions_ms: [], status: 'aborted', reason: '', comprehension: '',
        regions: task.tile_ids.map(tile => ({tile_id: tile,
          baseline_count: asset.regions.find(region => region.id === tile).baseline_count,
          entered_count: null, uncertainty: null, confirmed: false, status: 'not_started', reason: ''}))};
      $('integrity').textContent = loaded.sealed ? 'Asset SHA-256 matches the public seal. This checks integrity, not participant identity.' :
        'No public asset seal supplied. Assignment hashes and asset identity metadata validated; file authenticity is not established.';
      $('comprehension').value = ''; $('task-reason').value = '';
      $('baseline-visible').checked = true; $('alternative').replaceChildren(new Option('Baseline only', '0'));
      if (task.arm_id === 'B') for (let run = 1; run <= 8; run++) $('alternative').add(new Option(`Alternative ${run}`, String(run)));
      $('alternative-label').hidden = task.arm_id === 'A';
      $('alternative').disabled = task.arm_id === 'A';
      renderTiles(); renderViewer(); $('exercise').hidden = false;
      $('task-state').textContent = 'All assets loaded and decoded. Press Start task when ready; no timing has started.';
      $('start').disabled = false; setEntryEnabled(false);
    } catch (error) {
      showError(error);
      $('task-state').textContent = 'Asset loading failed before timing began. No task record was fabricated. This assignment remains unstarted/missing.';
      $('next').hidden = false; $('next').textContent = 'Retry loading this task';
      // The retry button is outside the hidden viewer so recovery stays reachable.
      $('session').append($('next'));
    } finally {state.loading = false;}
  }
  function setEntryEnabled(enabled) {
    $('tiles').querySelectorAll('input,select,textarea,.confirm-tile').forEach(element => {element.disabled = !enabled;});
    $('comprehension').disabled = !enabled; $('task-reason').disabled = !enabled;
    $('exercise').querySelector('.layout').hidden = !state.started;
    $('exercise').querySelector('.viewer-controls').hidden = !state.started;
    for (const id of ['baseline-visible', 'full-field']) $(id).disabled = !enabled;
    $('alternative').disabled = !enabled || state.asset?.arm_id === 'A';
    $('tiles').querySelectorAll('.inspect-tile').forEach(element => {element.disabled = !enabled;});
    for (const id of ['complete', 'incomplete', 'abort', 'fail']) $(id).disabled = !enabled;
    $('stop').disabled = state.stopped || state.loading;
  }
  function resetRegion(region) {region.confirmed = false; region.status = 'not_started';}
  function tileStatus(region, card) {
    card.querySelector('.tile-status').textContent = region.status === 'completed' ? 'Confirmed' :
      region.status === 'unresolved' ? 'Unresolved' : (region.entered_count !== null || region.uncertainty !== null ? 'Partial / unconfirmed' : 'Not started');
  }
  function renderTiles() {
    $('tiles').replaceChildren();
    for (const [index, region] of state.draft.regions.entries()) {
      const card = text('article', '', 'tile'); card.dataset.tileId = region.tile_id;
      const heading = text('div', '', 'tile-header');
      heading.append(text('h3', `Assigned tile ${index + 1} of 4 · tile ${region.tile_id + 1}`));
      const inspect = text('button', 'Inspect tile', 'inspect-tile'); inspect.type = 'button';
      inspect.setAttribute('aria-label', `Inspect tile ${region.tile_id + 1}`);
      inspect.addEventListener('click', () => {state.selectedTile = region.tile_id; state.fullField = false; renderViewer();});
      heading.append(inspect); card.append(heading);
      const badge = text('p', 'Not started', 'tile-status'); badge.setAttribute('role', 'status'); card.append(badge);
      const countLabel = text('label', 'Your tally (0–1000)');
      const count = document.createElement('input'); count.type = 'number'; count.min = '0'; count.max = '1000'; count.step = '1';
      count.inputMode = 'numeric'; count.id = `count-${region.tile_id}`; countLabel.htmlFor = count.id;
      countLabel.append(count); card.append(countLabel);
      const uncertaintyLabel = text('label', 'Uncertainty');
      const uncertainty = document.createElement('select'); uncertainty.id = `uncertainty-${region.tile_id}`;
      uncertaintyLabel.htmlFor = uncertainty.id;
      uncertainty.add(new Option('Choose uncertainty', ''));
      ['0 · None reported', '1 · Low', '2 · Moderate', '3 · High'].forEach((label, value) => uncertainty.add(new Option(label, String(value))));
      uncertaintyLabel.append(uncertainty); card.append(uncertaintyLabel);
      const unresolvedLabel = text('label', 'Mark unresolved');
      const unresolved = document.createElement('input'); unresolved.type = 'checkbox'; unresolved.id = `unresolved-${region.tile_id}`;
      unresolvedLabel.htmlFor = unresolved.id; unresolvedLabel.prepend(unresolved); card.append(unresolvedLabel);
      const reasonLabel = text('label', 'Unresolved / partial-entry reason (no personal details)', 'reason-label');
      const reason = document.createElement('textarea'); reason.id = `reason-${region.tile_id}`; reason.maxLength = 500; reason.rows = 2;
      reasonLabel.htmlFor = reason.id; reasonLabel.append(reason); card.append(reasonLabel);
      const confirm = text('button', 'Confirm tile', 'confirm-tile'); confirm.type = 'button';
      confirm.setAttribute('aria-label', `Confirm tile ${region.tile_id + 1}`); card.append(confirm);
      const update = () => {
        resetRegion(region);
        region.entered_count = /^\d+$/.test(count.value) ? Number(count.value) : null;
        region.uncertainty = uncertainty.value === '' ? null : Number(uncertainty.value);
        region.reason = reason.value.slice(0, 500);
        if (unresolved.checked) region.status = 'unresolved';
        tileStatus(region, card);
      };
      count.addEventListener('input', update); uncertainty.addEventListener('change', update);
      unresolved.addEventListener('change', update); reason.addEventListener('input', update);
      card.addEventListener('focusin', () => {
        if (state.selectedTile !== region.tile_id) {state.selectedTile = region.tile_id; renderViewer();}
      });
      confirm.addEventListener('click', () => {
        clearError();
        try {
          require(state.started && !state.ended, 'Start the task before entering a confirmation');
          require(!unresolved.checked, 'An unresolved tile cannot be confirmed. Supply its reason and finish the task as incomplete.');
          require(count.validity.valid && integer(region.entered_count, 0, 1000), 'Enter a whole tally from 0 to 1000');
          require(integer(region.uncertainty, 0, 3), 'Choose uncertainty before confirming');
          region.confirmed = true; region.status = 'completed'; tileStatus(region, card);
        } catch (error) {showError(error);}
      });
      $('tiles').append(card);
    }
  }
  const svgElement = (tag, attributes) => {
    const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
    return element;
  };
  function renderViewer() {
    if (!state.asset) return;
    const asset = state.asset, region = asset.regions.find(region => region.id === state.selectedTile);
    const box = state.fullField ? [0, 0, asset.width, asset.height] : region.bbox;
    $('viewer').setAttribute('viewBox', `${box[0]} ${box[1]} ${box[2] - box[0]} ${box[3] - box[1]}`);
    $('viewer').setAttribute('width', asset.width); $('viewer').setAttribute('height', asset.height);
    $('viewer').setAttribute('aria-label', `Actual microscopy ${state.fullField ? 'field' : `tile ${region.id + 1}`} with selected outline view`);
    $('viewer').replaceChildren();
    const addImage = (png, layer) => $('viewer').append(svgElement('image', {x: 0, y: 0,
      width: asset.width, height: asset.height, href: `data:image/png;base64,${png}`, 'data-layer': layer}));
    addImage(asset.image_png, 'image');
    if ($('baseline-visible').checked) addImage(asset.baseline_outline_png, 'baseline');
    const run = Number($('alternative').value);
    if (asset.arm_id === 'B' && run > 0) addImage(asset.alternative_outline_pngs[run - 1], `alternative-${run}`);
    for (const tile of state.draft.tile_ids) {
      const bounds = asset.regions.find(region => region.id === tile).bbox;
      $('viewer').append(svgElement('rect', {x: bounds[0] + .5, y: bounds[1] + .5,
        width: bounds[2] - bounds[0] - 1, height: bounds[3] - bounds[1] - 1, fill: 'none',
        stroke: tile === state.selectedTile ? '#ffe183' : '#edf3ff', 'stroke-width': tile === state.selectedTile ? 2 : 1,
        'vector-effect': 'non-scaling-stroke', 'data-tile-id': tile}));
    }
    $('tiles').querySelectorAll('.tile').forEach(card => card.classList.toggle('active', Number(card.dataset.tileId) === state.selectedTile));
    $('full-field').textContent = state.fullField ? 'Zoom to selected tile' : 'Show full field';
    $('full-field').setAttribute('aria-pressed', String(state.fullField));
    $('viewer-caption').textContent = `View ${asset.arm_id} · ${asset.field_id} · tile ${region.id + 1}. Outlines do not establish correctness. Count by nucleus center; do not count objects solely because their boundary touches this tile.`;
    if (asset.arm_id === 'B' && run > 0) {
      const events = region.events.filter(event => event.run_id === run);
      $('events').textContent = `Alternative ${run}: ${region.run_counts[run]} nuclei with centers in this tile. ` +
        (events.length ? events.map(event => `${event.kind}: ${event.baseline_count} → ${event.alternate_count}`).join('; ') : 'No count-changing component listed for this tile.') +
        ' Components can cross tile boundaries. These are disagreements, not verified errors.';
    } else $('events').textContent = 'Inspect the real image and baseline outlines. Enter your own tally; uncertainty is allowed.';
  }
  function startTask() {
    clearError();
    try {
      require(state.asset && !state.loading && !state.started && !state.stopped, 'Load the assets before starting');
      state.draft.started_at = new Date().toISOString(); state.startMono = performance.now();
      state.started = true; $('start').disabled = true; setEntryEnabled(true);
      if (document.hidden) state.draft.visibility_interruptions_ms.push(0);
      updateTaskState(); state.timer = setInterval(updateTaskState, 250);
    } catch (error) {showError(error);}
  }
  function snapshot(status, reason) {
    const duration = elapsed(), ended = new Date().toISOString();
    require(Date.parse(ended) >= Date.parse(state.draft.started_at), 'System clock moved backwards; timestamps cannot be safely exported');
    const regions = structuredClone(state.draft.regions);
    for (const region of regions) {
      require(region.entered_count === null || integer(region.entered_count, 0, 1000), 'Remove or correct a tally outside 0–1000 before export');
      require(region.uncertainty === null || integer(region.uncertainty, 0, 3), 'Invalid uncertainty');
      require(region.status !== 'unresolved' || region.reason.trim(), 'Every unresolved tile requires a reason');
    }
    return {...structuredClone(state.draft), ended_at: ended, elapsed_ms: duration,
      visibility_interruptions_ms: [...state.draft.visibility_interruptions_ms], status, reason, regions,
      comprehension: $('comprehension').value.slice(0, 500)};
  }
  function finishTask(status) {
    clearError();
    try {
      require(state.started && !state.ended && !state.stopped, 'Start the task first');
      const reason = $('task-reason').value.trim().slice(0, 500);
      if (status === 'completed') require(state.draft.regions.every(region => region.status === 'completed' && region.confirmed), 'Confirm all four tiles, or finish as incomplete with a reason');
      else require(reason, 'Supply a reason for an incomplete, failed or aborted task');
      const record = snapshot(status, status === 'completed' ? '' : reason);
      if (state.practice) {
        require(status === 'completed', 'Complete all four practice tiles before assessment; you may stop or withdraw at any time');
        state.practiceDone = true;
      } else state.records.push(record);
      state.ended = true; clearInterval(state.timer); setEntryEnabled(false);
      $('task-state').textContent = state.practice ? 'Common practice completed; practice is not included in the assessment export.' :
        `Task ${state.index + 1} saved as ${status}. ${(record.elapsed_ms / 1000).toFixed(1)} seconds observed.`;
      $('progress').textContent = `${state.records.length} of 4 assessment tasks saved in memory.`;
      if (state.practice || state.index < state.assignments.length - 1) {
        $('next').hidden = false; $('next').textContent = state.practice ? 'Load first assessment task' : 'Load next task';
      } else {
        $('summary').hidden = false; $('summary').textContent = 'All four assigned tasks have records. Export JSON before leaving. This is not a claim of a human study.';
      }
    } catch (error) {showError(error);}
  }
  function stopExercise() {
    clearError();
    try {
      if (state.started && !state.ended && !state.practice) {
        const reason = $('task-reason').value.trim().slice(0, 500) || 'Participant stopped the exercise before finishing the task.';
        state.records.push(snapshot('aborted', reason));
      }
      state.stopped = true; state.ended = true; clearInterval(state.timer); setEntryEnabled(false);
      $('start').disabled = true; $('next').hidden = true;
      $('summary').hidden = false; $('summary').textContent = 'Exercise stopped voluntarily. Unstarted tasks remain omitted. Export the retained partial records before leaving, or withdraw to export a request only.';
      $('task-state').textContent = 'Stopped. No further timing or entries.';
    } catch (error) {showError(error);}
  }
  function withdraw() {
    state.retention = 'delete'; state.stopped = true; state.ended = true;
    clearInterval(state.timer); state.records = []; state.draft = null;
    $('exercise').hidden = true; $('next').hidden = true; $('summary').hidden = false;
    $('stop').disabled = true; $('withdraw').disabled = true;
    $('summary').textContent = 'Withdrawn. Export JSON creates a withdrawal request only, with no task data. This does not delete operator copies or existing downloads. Deliver the request to the operator and follow the agreed deletion process. Nothing was uploaded.';
    $('task-state').textContent = 'Withdrawal request ready. In-memory task records cleared.';
  }
  function exportRecord() {
    clearError();
    try {
      require(state.consent && state.participant, 'Acknowledge consent and select an assigned code first');
      let tasks = structuredClone(state.records);
      if (state.retention === 'delete') tasks = [];
      else if (state.started && !state.ended && !state.practice) {
        tasks.push(snapshot('aborted', 'Incomplete at export; task remains open in memory.'));
      }
      const record = {schema_version: 1, protocol_hash: state.manifest.protocol_hash,
        participant_id: state.participant, synthetic_test: synthetic, experience_band: state.experience,
        retention_choice: state.retention, consent_acknowledged: state.consent, tasks};
      require(sameKeys(Object.keys(record), state.contract.required_export_keys), 'Export contract mismatch');
      for (const task of tasks) {
        require(sameKeys(Object.keys(task), state.contract.required_task_keys), 'Task contract mismatch');
        require(task.regions.every(region => sameKeys(Object.keys(region), state.contract.required_region_keys)), 'Region contract mismatch');
      }
      const blob = new Blob([`${JSON.stringify(record, null, 2)}\n`], {type: 'application/json'});
      const url = URL.createObjectURL(blob), link = document.createElement('a');
      link.href = url; link.download = `${synthetic ? 'SYNTHETIC-' : ''}reader-${state.participant}${state.retention === 'delete' ? '-withdrawal-request' : ''}.json`;
      link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
      $('progress').textContent = state.retention === 'delete' ? 'Withdrawal request downloaded locally. No operator copies were deleted.' :
        `${tasks.length} started task records downloaded locally, including incomplete tasks. No automatic upload. Active tasks continue in memory.`;
    } catch (error) {showError(error);}
  }
  $('consent-form').addEventListener('submit', async event => {
    event.preventDefault(); clearError();
    try {
      require($('operator-ready').checked, 'Operator readiness must be checked before continuing');
      require($('consent').checked && state.manifest.assignments[$('participant').value], 'Choose an assigned code and acknowledge consent');
      require(['retain', 'delete'].includes($('retention').value), 'Make an explicit retention choice');
      state.participant = $('participant').value; state.experience = $('experience').value;
      state.retention = $('retention').value; state.consent = true;
      state.assignments = structuredClone(state.manifest.assignments[state.participant]);
      $('setup').hidden = true; $('session').hidden = false;
      if (state.retention === 'delete') withdraw(); else await loadTask();
    } catch (error) {showError(error);}
  });
  $('start').addEventListener('click', startTask);
  $('complete').addEventListener('click', () => finishTask('completed'));
  $('incomplete').addEventListener('click', () => finishTask('failed'));
  $('fail').addEventListener('click', () => finishTask('failed'));
  $('abort').addEventListener('click', () => finishTask('aborted'));
  $('next').addEventListener('click', async () => {
    if (state.loading || state.stopped) return;
    if (!state.asset) {await loadTask(); return;}
    if (!state.ended) return;
    if (state.practice) {state.practice = false; state.index = 0;} else state.index++;
    await loadTask();
  });
  $('export').addEventListener('click', exportRecord);
  $('stop').addEventListener('click', stopExercise);
  $('withdraw').addEventListener('click', withdraw);
  $('alternative').addEventListener('change', renderViewer);
  $('baseline-visible').addEventListener('change', renderViewer);
  $('full-field').addEventListener('click', () => {state.fullField = !state.fullField; renderViewer();});
  document.addEventListener('visibilitychange', () => {
    if (state.started && !state.ended && state.draft) {
      try {state.draft.visibility_interruptions_ms.push(elapsed());} catch (error) {showError(error);}
    }
  });
  addEventListener('beforeunload', event => {
    if (state.consent && state.retention === 'retain') {event.preventDefault(); event.returnValue = '';}
  });
  (async () => {
    try {
      require(['http:', 'https:'].includes(location.protocol), 'Open this bundle using a local HTTP server, not file://');
      state.manifest = (await loadJSON('manifest.json')).data;
      const contract = await loadJSON('export-contract.json'); state.contract = contract.data;
      await validateManifest(state.manifest, state.contract);
      for (const participant of Object.keys(state.manifest.assignments)) $('participant').add(new Option(participant, participant));
      $('loading').textContent = 'Local manifest and exact export contract validated. No session has started.';
      $('setup').hidden = false;
    } catch (error) {$('loading').textContent = 'Unable to prepare exercise. No session has started.'; showError(error);}
  })();
})();
