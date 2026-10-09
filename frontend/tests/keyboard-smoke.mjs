import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {inflateSync} from 'node:zlib';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {fromArrayBuffer} from 'geotiff';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const suffix = process.env.CI ? '-ci' : '';
const reportPath = path.join(root, `evaluation/checks/keyboard-smoke${suffix}.json`);
const artifactDir = path.join(root, `artifacts/keyboard-smoke${suffix}`);
const target = process.env.NUCLEILENS_DEMO_URL || 'http://127.0.0.1:5173';
const executable = process.env.NUCLEILENS_CHROMIUM_BIN ||
  (!process.env.CI && existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined);
const report = {status: 'running', target, tab_limit: 160, focus: [], steps: [],
  downloads: [], page_errors: [], console_errors: [], failed_requests: []};
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
let browser;
let page;

// DOM evaluation is observational only. Every interaction uses page.keyboard.
async function focusState() {
  return page.evaluate(() => {
    const el = document.activeElement;
    if (!(el instanceof HTMLElement)) return null;
    const style = getComputedStyle(el), rect = el.getBoundingClientRect();
    const transparent = color => color === 'transparent' || /rgba\([^)]*,\s*0\)$/.test(color);
    const outline = {style: style.outlineStyle, width: style.outlineWidth,
      color: style.outlineColor, offset: style.outlineOffset};
    const border = Object.fromEntries(['Top', 'Right', 'Bottom', 'Left'].map(side =>
      [side.toLowerCase(), {style: style[`border${side}Style`],
        width: style[`border${side}Width`], color: style[`border${side}Color`]}]));
    const x = Math.max(0, rect.left), y = Math.max(0, rect.top);
    const right = Math.min(innerWidth, rect.right), bottom = Math.min(innerHeight, rect.bottom);
    const hit = right > x && bottom > y ? document.elementFromPoint((x + right) / 2, (y + bottom) / 2) : null;
    const outlineVisible = !['none', 'hidden'].includes(outline.style) &&
      parseFloat(outline.width) >= 2 && !transparent(outline.color);
    return {tag: el.tagName.toLowerCase(), id: el.id,
      name: el.getAttribute('aria-label') || el.textContent?.trim().replace(/\s+/g, ' ').slice(0, 160),
      focus_visible: el.matches(':focus-visible'), outline, border,
      outline_visible: outlineVisible,
      visible: style.visibility === 'visible' && Number(style.opacity) > 0 &&
        rect.width > 1 && rect.height > 1 && right - x > 1 && bottom - y > 1 &&
        !!hit && (hit === el || el.contains(hit)),
      rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height}};
  });
}

async function reach(locator, label, reverse = false) {
  assert.equal(await locator.count(), 1, `${label}: expected one target`);
  assert.ok(await locator.isVisible(), `${label}: target is hidden`);
  assert.ok(await locator.isEnabled(), `${label}: target is disabled`);
  for (let tabs = 0; tabs <= report.tab_limit; tabs++) {
    if (await locator.evaluate(el => el === document.activeElement)) {
      const focused = await focusState();
      report.focus.push({target: label, direction: reverse ? 'Shift+Tab' : 'Tab', tabs, ...focused});
      assert.ok(focused?.visible, `${label}: focused target is obscured or outside the viewport`);
      assert.ok(focused.focus_visible && focused.outline_visible,
        `${label}: no visible keyboard outline (computed border recorded separately)`);
      return;
    }
    if (tabs < report.tab_limit) await page.keyboard.press(reverse ? 'Shift+Tab' : 'Tab');
  }
  throw new Error(`${label}: unreachable after ${report.tab_limit} ${reverse ? 'Shift+Tab' : 'Tab'} presses`);
}

const button = name => page.getByRole('button', {name, exact: true});
async function activate(name, key = 'Enter', reverse = false) {
  await reach(button(name), name, reverse);
  await page.keyboard.press(key);
  report.steps.push({action: name, key});
}

async function visibleText(locator, expected, label) {
  assert.ok(await locator.isVisible(), `${label}: not visible`);
  const text = (await locator.innerText()).replace(/\s+/g, ' ').trim();
  if (typeof expected === 'string') assert.equal(text, expected, label);
  else assert.match(text, expected, label);
  return text;
}

async function counts(maskCount, transition) {
  await page.waitForFunction(count =>
    document.querySelector('[data-testid="mask-count"]')?.textContent?.trim().startsWith(`${count} `), maskCount);
  const mask = await visibleText(page.getByTestId('mask-count'), `${maskCount} instances`, 'mask count');
  const strip = await visibleText(page.locator('.count-strip'),
    /^BASELINE COUNT 74 REVIEW TALLY TOTAL 74$/, 'independent count labels and values');
  await visibleText(page.getByTestId('measurement-summary').locator('div').first(),
    `Instances · original → reviewed 74 → ${maskCount}`, 'recalculated instance measurements');
  const status = await visibleText(page.locator('.mask-review [role="status"]'), transition ?
    new RegExp(`Mask: ${transition} instances\\. Review tally total remains 74; mask edits do not change tally entries\\.`) :
    /No mask edits\. Inspect an alternative before confirming it\./, 'accessible mask status');
  assert.equal(await page.getByRole('alert').count(), 0, 'unexpected visible error');
  report.steps.push({mask_count: maskCount, mask, count_semantics: strip, status});
}

async function download(name, filename) {
  await reach(button(name), name);
  const pending = page.waitForEvent('download');
  await page.keyboard.press('Enter');
  const item = await pending;
  assert.equal(await item.failure(), null, `${name}: download failed`);
  const destination = path.join(artifactDir, filename);
  await item.saveAs(destination);
  const bytes = await readFile(destination);
  assert.ok(bytes.length > 0, `${name}: empty download`);
  report.downloads.push({action: name, key: 'Enter', file: path.relative(root, destination),
    suggested_filename: item.suggestedFilename(), bytes: bytes.length, sha256: hash(bytes)});
  return bytes;
}

async function labels(bytes, count, reference) {
  const tiff = await fromArrayBuffer(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
  const image = await tiff.getImage();
  assert.equal(image.getWidth(), reference.width);
  assert.equal(image.getHeight(), reference.height);
  assert.equal(image.getSamplesPerPixel(), 1);
  const pixels = await image.readRasters({interleave: true});
  assert.ok(pixels instanceof Uint32Array, 'TIFF must contain unsigned 32-bit instance labels');
  assert.equal(new Set(pixels.filter(id => id !== 0)).size, count, 'actual exported instance count');
  const result = Buffer.alloc(pixels.length * 4);
  pixels.forEach((id, index) => result.writeUInt32LE(id, index * 4));
  return result;
}

async function audit(expectedBytes, expectedChanges, expectedCount, filename) {
  const value = JSON.parse(await download('Export review JSON', filename));
  assert.equal(value.baseline_count, 74);
  assert.equal(value.reviewed_count, 74);
  assert.deepEqual(value.corrections, []);
  assert.equal(value.mask_review.count, expectedCount);
  assert.equal(value.mask_review.sha256_uint32_le, hash(expectedBytes));
  assert.equal(value.mask_review.changes.length, expectedChanges);
  assert.equal(value.mask_modifications, expectedChanges > 0);
  assert.match(value.mask_review.semantics, /Tally corrections.*do not modify this mask/);
  return value;
}

async function inspect(kind, witness, reference) {
  const event = witness[kind];
  await activate(`Inspect ${kind} · ${event.baseline_count} → ${event.alternate_count}`);
  await page.waitForFunction(run => document.querySelector('#alternative')?.value === String(run), witness.run);
  await visibleText(page.getByRole('region', {name: 'Same count counterexample'}),
    /74 nuclei\. In both runs\..*neither mask is automatically correct\./, 'visible split/merge witness');
  assert.equal(await button('Full field').getAttribute('aria-pressed'), 'true', 'inspect zoom state');
  const bbox = reference.regions.find(region => region.id === event.region_id).bbox;
  assert.equal(await page.locator('svg.microscopy').getAttribute('viewBox'),
    `${bbox[0]} ${bbox[1]} ${bbox[2] - bbox[0]} ${bbox[3] - bbox[1]}`, 'inspected actual region');
  const proposal = `Confirm ${event.kind} · ${event.baseline_count} → ${event.alternate_count}`;
  assert.ok(await button(proposal).isVisible(), 'inspected alternative is available for confirmation');
  return proposal;
}

try {
  // This script intentionally permits only an owned loopback preview, including when overridden.
  const url = new URL(target);
  assert.ok(['http:', 'https:'].includes(url.protocol) &&
    ['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname) && !url.username && !url.password,
  'NUCLEILENS_DEMO_URL must be a local preview without credentials');
  await mkdir(artifactDir, {recursive: true});
  browser = await chromium.launch({executablePath: executable, headless: true, args: ['--no-sandbox']});
  page = await browser.newPage({viewport: {width: 1440, height: 1080}, acceptDownloads: true});
  page.setDefaultTimeout(15000);
  page.on('pageerror', error => report.page_errors.push(error.message));
  page.on('console', message => {if (message.type() === 'error') report.console_errors.push(message.text().slice(0, 500));});
  page.on('requestfailed', request => report.failed_requests.push({path: new URL(request.url()).pathname, error: request.failure()?.errorText}));
  // No external navigation or requests; no neural or classical inference is triggered.
  await page.route('**/*', route => {
    const requestURL = new URL(route.request().url());
    return requestURL.origin === url.origin || ['data:', 'blob:'].includes(requestURL.protocol)
      ? route.continue() : route.abort('blockedbyclient');
  });
  await page.goto(target);
  assert.equal(new URL(page.url()).origin, url.origin, 'preview redirected outside loopback origin');
  await page.waitForFunction(() => document.querySelector('[data-testid="mask-count"]')?.textContent?.trim().startsWith('74 '));
  const reference = JSON.parse(await readFile(path.join(root, 'frontend/public/samples/training-001.json'), 'utf8'));
  const baseline = inflateSync(Buffer.from(reference.label_maps.runs[0], 'base64'));
  assert.equal(reference.raw_count, 74);
  const run = reference.run_counts.findIndex((count, index) => index > 0 && count === 74 &&
    ['split alternative', 'merge alternative'].every(kind => reference.regions.some(region =>
      region.events.some(event => event.run_id === index && event.kind === kind))));
  assert.ok(run > 0, 'actual equal-total split/merge witness missing');
  const events = reference.regions.flatMap(region => region.events.filter(event => event.run_id === run)
    .map(event => ({...event, region_id: region.id})));
  const witness = {run, split: events.find(event => event.kind === 'split alternative'),
    merge: events.find(event => event.kind === 'merge alternative')};
  assert.equal(witness.split.alternate_count - witness.split.baseline_count, 1);
  assert.equal(witness.merge.alternate_count - witness.merge.baseline_count, -1);

  // Sample buttons are the application's actual sample selector.
  await activate('Dense field BBBC039', 'Space');
  await page.waitForFunction(() => document.querySelector('.sample.selected')?.textContent?.startsWith('Dense field') &&
    document.querySelector('.status-row')?.textContent?.includes('Real reference run'));
  await activate('First training field BBBC039', 'Enter', true);
  await page.waitForFunction(() => document.querySelector('.sample.selected')?.textContent?.startsWith('First training field') &&
    document.querySelector('[data-testid="mask-count"]')?.textContent?.trim().startsWith('74 '));
  await visibleText(page.locator('.status-row[role="status"]'), /Real reference run · rerun to verify on your device/, 'sample load status');
  await counts(74);

  await reach(page.getByLabel('Compare a sensitivity run'), 'sensitivity selector');
  await page.keyboard.press('Home');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  assert.equal(await page.getByLabel('Compare a sensitivity run').inputValue(), '1', 'keyboard select changed actual run');
  await page.keyboard.press('Home');
  await page.keyboard.press('Enter');
  assert.equal(await page.getByLabel('Compare a sensitivity run').inputValue(), '0', 'keyboard select restored baseline run');
  report.steps.push({action: 'sensitivity selector', keys: ['Home', 'ArrowDown', 'Enter', 'Home', 'Enter'], values: [1, 0]});

  const splitProposal = await inspect('split', witness, reference);
  await activate(splitProposal, 'Space');
  await counts(75, '74 → 75');
  const splitBytes = await labels(await download('Export label TIFF', 'split.tif'), 75, reference);
  assert.ok(!splitBytes.equals(baseline), 'split must change actual pixels');
  const splitAudit = await audit(splitBytes, 1, 75, 'split.json');
  assert.deepEqual(splitAudit.mask_review.changes[0].event, reference.regions
    .find(region => region.id === witness.split.region_id).events.find(event => event.run_id === run && event.kind === witness.split.kind));

  const mergeProposal = await inspect('merge', witness, reference);
  await activate(mergeProposal);
  await counts(74, '75 → 74');
  await visibleText(page.locator('.quality-review .partition-status[role="status"]'),
    /same total but a different segmentation\. Equal counts do not establish equal accuracy\./, 'equal-total limitation');
  const mergedBytes = await labels(await download('Export label TIFF', 'split-merge.tif'), 74, reference);
  assert.ok(!mergedBytes.equals(baseline), 'equal-total edits must change pixels');
  const mergedAudit = await audit(mergedBytes, 2, 74, 'split-merge.json');
  assert.deepEqual(mergedAudit.mask_review.changes.map(change => [change.before_count, change.after_count]), [[74, 75], [75, 74]]);
  assert.deepEqual(mergedAudit.mask_review.changes[1].event, reference.regions
    .find(region => region.id === witness.merge.region_id).events.find(event => event.run_id === run && event.kind === witness.merge.kind));
  assert.ok(mergedAudit.mask_review.changes.every(change => change.changed_pixels > 0));

  await activate('Undo mask edit', 'Space', true);
  await counts(75, '74 → 75');
  const undoMerge = await labels(await download('Export label TIFF', 'undo-merge.tif'), 75, reference);
  assert.ok(undoMerge.equals(splitBytes), 'first undo must restore exact split pixels');
  await activate('Undo mask edit', 'Enter', true);
  await counts(74, '75 → 74');
  assert.ok(await button('Undo mask edit').isDisabled(), 'mask history must be empty');
  const restored = await labels(await download('Export label TIFF', 'restored.tif'), 74, reference);
  assert.ok(restored.equals(baseline), 'second undo must restore every baseline label byte');
  await audit(restored, 0, 74, 'restored.json');
  await visibleText(page.locator('.quality-review .partition-status[role="status"]'),
    /Reviewed and original segmentations match, allowing harmless label-ID renumbering\./, 'restored segmentation status');
  assert.deepEqual(report.page_errors, [], 'browser runtime errors');
  Object.assign(report, {status: 'passed', sample_selection_keyboard: true,
    sensitivity_selection_keyboard: true, witness_inspection_keyboard: true,
    mask_counts: [74, 75, 74], undo_counts: [75, 74], exact_undo: true,
    json_hash_verified: true, uint32_tiff_verified: true, baseline_sha256: hash(baseline)});
  console.log('PASS: keyboard samples, witness, real mask 74→75→74, exact undo, JSON/TIFF.');
} catch (error) {
  report.status = 'failed';
  report.error = {name: error.name, message: error.message};
  report.active_element = page ? await focusState().catch(() => null) : null;
  report.visible_status = page ? await page.locator('.status-row').innerText().catch(() => null) : null;
  process.exitCode = 1;
  console.error(`FAIL: ${error.message}`);
} finally {
  if (browser) await browser.close().catch(error => {
    report.status = 'failed'; report.close_error = error.message; process.exitCode = 1;
  });
  await mkdir(path.dirname(reportPath), {recursive: true});
  await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
}
