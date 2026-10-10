// Synthetic software validation only. Downloads remain in memory unless an explicit temporary output is supplied.
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {readFile, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';

let playwright;
try {playwright = createRequire(import.meta.url)('playwright');}
catch (error) {
  if (error.code !== 'MODULE_NOT_FOUND') throw error;
  playwright = createRequire(process.env.NUCLEILENS_READER_DEPS_PACKAGE ||
    new URL('../frontend/package.json', import.meta.url))('playwright');
}
const {chromium} = playwright;

const target = new URL(process.env.NUCLEILENS_READER_URL || 'http://127.0.0.1:5181');
assert.ok(['http:', 'https:'].includes(target.protocol) && ['127.0.0.1', 'localhost', '[::1]'].includes(target.hostname) &&
  !target.username && !target.password, 'Tests require an owned loopback bundle');
target.searchParams.set('test', '1');
const executable = process.env.NUCLEILENS_CHROMIUM_BIN ||
  (!process.env.CI && existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined);
const summary = {synthetic_test: true, evidence_label: 'SYNTHETIC SOFTWARE TEST — NOT HUMAN OBSERVATIONS',
  target: target.href, checks: [], page_errors: [], external_requests: [], requested_assets: []};
let browser;
const pages = [];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const publicURL = filename => new URL(filename, target).href;
const sortedKeys = value => Object.keys(value).sort();
async function newPage() {
  const page = await browser.newPage({viewport: {width: 1440, height: 1080}, acceptDownloads: true});
  pages.push(page); page.setDefaultTimeout(15000);
  page.on('pageerror', error => summary.page_errors.push(error.message));
  page.on('request', request => {
    const url = new URL(request.url());
    if (['http:', 'https:'].includes(url.protocol)) {
      if (url.origin !== target.origin) summary.external_requests.push(url.origin);
      else summary.requested_assets.push(url.pathname.split('/').pop());
    }
  });
  await page.route('**/*', route => {
    const url = new URL(route.request().url());
    return url.origin === target.origin || ['data:', 'blob:'].includes(url.protocol) ? route.continue() : route.abort();
  });
  return page;
}
async function open(page) {
  await page.goto(target.href);
  await page.locator('#setup').waitFor({state: 'visible'});
  assert.match(await page.locator('#synthetic').innerText(), /^SYNTHETIC SOFTWARE TEST/);
  assert.ok(await page.locator('#synthetic').isVisible());
}
async function consent(page, participant = 'P01', retention = 'retain') {
  await page.locator('#participant').selectOption(participant);
  await page.locator('#retention').selectOption(retention);
  await page.locator('#consent').check();
  // Verify the independent operator gate before acknowledging software readiness.
  await page.getByRole('button', {name: 'Continue to common practice', exact: true}).click();
  assert.match(await page.getByRole('alert').innerText(), /Operator readiness/);
  await page.locator('#operator-ready').check();
  await page.getByRole('button', {name: 'Continue to common practice', exact: true}).click();
  if (retention === 'retain') await ready(page);
  else await page.locator('#summary').waitFor({state: 'visible'});
}
async function ready(page) {
  await page.waitForFunction(() => document.querySelector('#task-state')?.textContent?.includes('All assets loaded and decoded.'));
  assert.ok(await page.locator('#start').isEnabled());
  assert.ok(await page.locator('.layout').isHidden(), 'assessment cannot be viewed before timing starts');
}
async function jsonDownload(page) {
  const pending = page.waitForEvent('download');
  await page.getByRole('button', {name: 'Export JSON', exact: true}).click();
  const download = await pending;
  assert.equal(await download.failure(), null);
  assert.match(download.suggestedFilename(), /^SYNTHETIC-reader-P0[1-6]/);
  const record = JSON.parse(await readFile(await download.path(), 'utf8'));
  assert.equal(record.synthetic_test, true, 'All automated exports MUST be synthetic');
  return record;
}
async function fillTile(page, tile, count = '3') {
  await page.locator(`#count-${tile}`).fill(count);
  await page.locator(`#uncertainty-${tile}`).selectOption('1');
  await page.getByRole('button', {name: `Confirm tile ${tile + 1}`, exact: true}).click();
  assert.equal(await page.locator(`[data-tile-id="${tile}"].tile .tile-status`).innerText(), 'Confirmed');
}
async function keyboardReach(page, locator) {
  for (let tabs = 0; tabs <= 180; tabs++) {
    if (await locator.evaluate(element => element === document.activeElement)) {
      const focused = await locator.evaluate(element => {
        const style = getComputedStyle(element), rect = element.getBoundingClientRect();
        return {focusVisible: element.matches(':focus-visible'), width: parseFloat(style.outlineWidth),
          style: style.outlineStyle, visible: rect.width > 1 && rect.height > 1 && rect.bottom > 0 && rect.top < innerHeight};
      });
      assert.ok(focused.focusVisible && focused.width >= 3 && focused.style !== 'none' && focused.visible);
      return;
    }
    if (tabs < 180) await page.keyboard.press('Tab');
  }
  throw new Error('Keyboard target unreachable in 180 tabs');
}
async function practice(page) {
  await page.locator('#start').click();
  await page.locator('.layout').waitFor({state: 'visible'});
  for (const tile of [0, 1, 2, 3]) await fillTile(page, tile);
  await page.locator('#complete').click();
  assert.match(await page.locator('#task-state').innerText(), /Common practice completed/);
  const exportAfterPractice = await jsonDownload(page);
  assert.deepEqual(exportAfterPractice.tasks, [], 'practice does not contaminate assessment records');
  await page.locator('#next').click(); await ready(page);
}
function validate(record, manifest, contract) {
  assert.deepEqual(sortedKeys(record), [...contract.required_export_keys].sort());
  assert.equal(record.schema_version, 1); assert.equal(record.protocol_hash, manifest.protocol_hash);
  assert.equal(record.consent_acknowledged, true); assert.equal(record.synthetic_test, true);
  assert.ok(contract.experience_band.includes(record.experience_band));
  assert.ok(contract.retention_choice.includes(record.retention_choice));
  for (const task of record.tasks) {
    assert.deepEqual(sortedKeys(task), [...contract.required_task_keys].sort());
    const assignment = manifest.assignments[record.participant_id].find(assignment => assignment.task_id === task.task_id);
    assert.ok(assignment);
    for (const [key, value] of Object.entries(assignment)) assert.deepEqual(task[key], value);
    assert.match(task.started_at, /Z$/); assert.match(task.ended_at, /Z$/);
    assert.ok(Date.parse(task.ended_at) >= Date.parse(task.started_at));
    assert.ok(Number.isInteger(task.elapsed_ms) && task.elapsed_ms >= 0 && task.elapsed_ms <= 86400000);
    assert.ok(task.visibility_interruptions_ms.every(value => Number.isInteger(value) && value >= 0 && value <= task.elapsed_ms));
    assert.deepEqual(task.visibility_interruptions_ms, [...task.visibility_interruptions_ms].sort((a, b) => a - b));
    assert.ok(contract.task_status.includes(task.status));
    assert.ok(typeof task.comprehension === 'string' && task.comprehension.length <= 500);
    assert.ok(typeof task.reason === 'string' && task.reason.length <= 500);
    if (task.status !== 'completed') assert.ok(task.reason.trim());
    assert.equal(task.regions.length, 4);
    assert.deepEqual(task.regions.map(region => region.tile_id), assignment.tile_ids);
    for (const region of task.regions) {
      assert.deepEqual(sortedKeys(region), [...contract.required_region_keys].sort());
      assert.ok(contract.region_status.includes(region.status));
      for (const [key, high] of [['baseline_count', 1000], ['entered_count', 1000], ['uncertainty', 3]]) {
        assert.ok(region[key] === null || (Number.isInteger(region[key]) && region[key] >= 0 && region[key] <= high));
      }
      if (region.status === 'completed') {
        assert.equal(region.confirmed, true); assert.notEqual(region.entered_count, null); assert.notEqual(region.uncertainty, null);
      } else {assert.equal(region.confirmed, false); assert.notEqual(task.status, 'completed');}
      if (region.status === 'unresolved') assert.ok(region.reason.trim());
    }
  }
}

try {
  browser = await chromium.launch({executablePath: executable, headless: true, args: ['--no-sandbox']});
  const page = await newPage();
  // API reads use only the same public bundle, never private/scoring data.
  const manifestResponse = await page.request.get(publicURL('manifest.json'));
  assert.ok(manifestResponse.ok(), 'Generator must have produced the served bundle');
  const manifest = await manifestResponse.json();
  const contract = await (await page.request.get(publicURL('export-contract.json'))).json();
  await open(page); await consent(page); await practice(page);
  summary.checks.push('synthetic label, consent/operator gates, decoded assets before timing, common practice excluded');

  for (const [index, assignment] of manifest.assignments.P01.entries()) {
    const asset = await (await page.request.get(publicURL(`${assignment.field_id}-${assignment.arm_id}.json`))).json();
    assert.equal(await page.locator('.tile').count(), 4);
    assert.deepEqual(await page.locator('.tile').evaluateAll(tiles => tiles.map(tile => Number(tile.dataset.tileId))), assignment.tile_ids);
    await keyboardReach(page, page.locator('#start'));
    await page.keyboard.press('Enter');
    await page.locator('.layout').waitFor({state: 'visible'});
    assert.equal(await page.locator('#viewer image[data-layer="image"]').getAttribute('href'), `data:image/png;base64,${asset.image_png}`);
    assert.equal(await page.locator('#viewer image[data-layer="baseline"]').getAttribute('href'), `data:image/png;base64,${asset.baseline_outline_png}`);
    if (assignment.arm_id === 'A') {
      assert.ok(await page.locator('#alternative-label').isHidden());
      assert.equal(await page.locator('#viewer image').count(), 2);
    } else {
      await keyboardReach(page, page.locator('#alternative'));
      await page.keyboard.press('Home'); await page.keyboard.press('ArrowDown'); await page.keyboard.press('Enter');
      assert.equal(await page.locator('#alternative').inputValue(), '1');
      assert.equal(await page.locator('#viewer image[data-layer="alternative-1"]').getAttribute('href'), `data:image/png;base64,${asset.alternative_outline_pngs[0]}`);
      await page.locator('#alternative').selectOption('8');
      assert.equal(await page.locator('#viewer image[data-layer="alternative-8"]').getAttribute('href'), `data:image/png;base64,${asset.alternative_outline_pngs[7]}`);
      assert.match(await page.locator('#events').innerText(), /disagreements, not verified errors/);
    }
    const firstTile = assignment.tile_ids[0];
    await page.getByRole('button', {name: `Inspect tile ${firstTile + 1}`, exact: true}).click();
    const bounds = asset.regions.find(region => region.id === firstTile).bbox;
    assert.equal(await page.locator('#viewer').getAttribute('viewBox'), `${bounds[0]} ${bounds[1]} ${bounds[2] - bounds[0]} ${bounds[3] - bounds[1]}`);
    await page.locator('#comprehension').fill('SYNTHETIC SOFTWARE TEST: outlines are proposals, not verified answers.');
    if (index === 0) {
      await page.locator(`#count-${firstTile}`).fill('1001');
      await page.locator(`#uncertainty-${firstTile}`).selectOption('2');
      await page.getByRole('button', {name: `Confirm tile ${firstTile + 1}`, exact: true}).click();
      assert.match(await page.getByRole('alert').innerText(), /0 to 1000/);
      await page.locator(`#count-${firstTile}`).fill('1.5');
      await page.getByRole('button', {name: `Confirm tile ${firstTile + 1}`, exact: true}).click();
      assert.match(await page.getByRole('alert').innerText(), /whole tally/);
      for (const tile of assignment.tile_ids) await fillTile(page, tile);
      await page.locator('#complete').click();
    } else if (index === 1) {
      await page.locator(`#count-${firstTile}`).fill('4');
      await page.locator(`#uncertainty-${firstTile}`).selectOption('3');
      await page.locator(`#unresolved-${firstTile}`).check();
      await page.locator(`#reason-${firstTile}`).fill('SYNTHETIC unresolved border object');
      await page.locator('#task-reason').fill('SYNTHETIC task includes unresolved tile');
      await page.locator('#incomplete').click();
    } else if (index === 2) {
      await page.locator(`#count-${firstTile}`).fill('5');
      // Explicit synthetic visibility event: headless lifecycle freezing does not
      // guarantee a visibilitychange event. This checks the listener, not real
      // tab-background behavior or a human interruption.
      await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
      const partial = await jsonDownload(page); validate(partial, manifest, contract);
      assert.equal(partial.tasks.length, 3);
      assert.equal(partial.tasks[2].status, 'aborted');
      assert.equal(partial.tasks[2].regions[0].entered_count, 5);
      assert.equal(partial.tasks[2].regions[0].confirmed, false);
      assert.match(partial.tasks[2].reason, /Incomplete at export/);
      assert.ok(partial.tasks[2].visibility_interruptions_ms.length >= 1, 'Synthetic visibility event must be recorded');
      await page.locator('#task-reason').fill('SYNTHETIC voluntary task abort');
      await page.locator('#abort').click();
    } else {
      await page.locator('#task-reason').fill('SYNTHETIC reported task failure');
      await page.locator('#fail').click();
    }
    if (index < 3) {await page.locator('#next').click(); await ready(page);}
  }
  const completed = await jsonDownload(page); validate(completed, manifest, contract);
  if (process.env.NUCLEILENS_READER_SYNTHETIC_EXPORT) {
    const output = resolve(process.env.NUCLEILENS_READER_SYNTHETIC_EXPORT);
    assert.ok(output.startsWith('/tmp/'), 'Synthetic integration exports must be temporary');
    assert.equal(completed.synthetic_test, true);
    await writeFile(output, JSON.stringify(completed), {flag: 'wx', mode: 0o600});
  }
  assert.deepEqual(completed.tasks.map(task => task.status), ['completed', 'failed', 'aborted', 'failed']);
  assert.equal(completed.tasks[1].regions[0].status, 'unresolved');
  assert.ok(completed.tasks.every(task => task.elapsed_ms > 0));
  for (const task of completed.tasks) {
    const asset = await (await page.request.get(publicURL(`${task.field_id}-${task.arm_id}.json`))).json();
    task.regions.forEach(region => assert.equal(region.baseline_count, asset.regions.find(tile => tile.id === region.tile_id).baseline_count));
  }
  summary.checks.push('actual A/B baseline and eight alternative assets, assigned tiles, keyboard focus, bounded tallies, completed/unresolved/aborted/failed records, active snapshot, exact schema and baselines');
  await page.setViewportSize({width: 390, height: 844});
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'mobile overflow');
  await page.locator('#withdraw').click();
  assert.match(await page.locator('#summary').innerText(), /does not delete operator copies/);
  const withdrawn = await jsonDownload(page); validate(withdrawn, manifest, contract);
  assert.equal(withdrawn.retention_choice, 'delete'); assert.deepEqual(withdrawn.tasks, []);
  summary.checks.push('responsive layout, withdrawal request only, no deletion claim');

  const withdrawalOnly = await newPage(); await open(withdrawalOnly); await consent(withdrawalOnly, 'P02', 'delete');
  const requestOnly = await jsonDownload(withdrawalOnly); validate(requestOnly, manifest, contract);
  assert.deepEqual(requestOnly.tasks, []);
  assert.ok(await withdrawalOnly.locator('#exercise').isHidden());

  const delayed = await newPage();
  let releaseAsset;
  const barrier = new Promise(resolve => {releaseAsset = resolve;});
  await delayed.route('**/Q01-B.json', async route => {await barrier; await route.continue();});
  await open(delayed);
  await delayed.locator('#participant').selectOption('P03'); await delayed.locator('#retention').selectOption('retain');
  await delayed.locator('#consent').check(); await delayed.locator('#operator-ready').check();
  await delayed.locator('#continue').click();
  await delayed.waitForFunction(() => document.querySelector('#task-state')?.textContent?.includes('Timing has not started.'));
  const emptyWhileLoading = await jsonDownload(delayed); validate(emptyWhileLoading, manifest, contract);
  assert.deepEqual(emptyWhileLoading.tasks, []);
  releaseAsset(); await ready(delayed);
  await delayed.locator('#start').click();
  await delayed.locator('#stop').click();
  const practiceStopped = await jsonDownload(delayed); validate(practiceStopped, manifest, contract);
  assert.deepEqual(practiceStopped.tasks, []);
  summary.checks.push('asset barrier prevents fabricated timing, voluntary practice stop, unstarted assessments omitted');

  const loadingFailure = await newPage();
  await loadingFailure.route('**/Q01-B.json', route => route.fulfill({status: 503, body: 'SYNTHETIC SOFTWARE TEST asset failure'}));
  await open(loadingFailure); await loadingFailure.locator('#participant').selectOption('P04');
  await loadingFailure.locator('#retention').selectOption('retain'); await loadingFailure.locator('#consent').check();
  await loadingFailure.locator('#operator-ready').check(); await loadingFailure.locator('#continue').click();
  await loadingFailure.getByRole('alert').waitFor({state: 'visible'});
  assert.match(await loadingFailure.locator('#task-state').innerText(), /No task record was fabricated/);
  assert.ok(await loadingFailure.locator('#next').isVisible());
  assert.deepEqual((await jsonDownload(loadingFailure)).tasks, []);

  const hashFailure = await newPage();
  // Expose an intentionally wrong public seal in this synthetic browser response only.
  await hashFailure.route('**/manifest.json', async route => {
    const response = await route.fetch(), altered = await response.json();
    altered.asset_sha256 = {'Q01-B.json': '0'.repeat(64)};
    await route.fulfill({response, json: altered});
  });
  await open(hashFailure); await hashFailure.locator('#participant').selectOption('P05');
  await hashFailure.locator('#retention').selectOption('retain'); await hashFailure.locator('#consent').check();
  await hashFailure.locator('#operator-ready').check(); await hashFailure.locator('#continue').click();
  await hashFailure.getByRole('alert').waitFor({state: 'visible'});
  assert.match(await hashFailure.getByRole('alert').innerText(), /SHA-256 mismatch/);

  const hashSuccess = await newPage();
  const practiceBytes = await (await hashSuccess.request.get(publicURL('Q01-B.json'))).body();
  await hashSuccess.route('**/manifest.json', async route => {
    const response = await route.fetch(), altered = await response.json();
    altered.asset_sha256 = {'Q01-B.json': hash(practiceBytes)};
    await route.fulfill({response, json: altered});
  });
  await open(hashSuccess); await consent(hashSuccess, 'P06');
  assert.match(await hashSuccess.locator('#integrity').innerText(), /matches the public seal/);
  summary.checks.push('asset-load error and reachable retry, public SHA-256 success/mismatch using actual bytes');

  assert.deepEqual(summary.page_errors, []); assert.deepEqual(summary.external_requests, []);
  const allowed = /^(?:|index\.html|app\.js|style\.css|manifest\.json|export-contract\.json|Q01-B\.json|F0[1-4]-[AB]\.json)$/;
  assert.ok(summary.requested_assets.every(name => allowed.test(name)), 'Unexpected/private/reference asset requested');
  summary.requested_assets = [...new Set(summary.requested_assets)].sort();
  summary.status = 'passed';
} catch (error) {
  summary.status = 'failed'; summary.error = {name: error.name, message: error.message};
  process.exitCode = 1;
} finally {
  if (browser) await browser.close().catch(error => {summary.status = 'failed'; summary.close_error = error.message; process.exitCode = 1;});
  console.log(JSON.stringify(summary, null, 2));
}
