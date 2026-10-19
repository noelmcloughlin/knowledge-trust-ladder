#!/usr/bin/env node
// Regenerates the Archify companions of this repository's figures.
//
// A companion is a traditional flow diagram of a figure in .assets/, for a
// reader who wants one beside the hand-made figure. Its source is an Archify
// candidate, .assets/companions/<name>.archify.json. This script renders it
// with the archify skill installed on this machine, exports the diagram in the
// light and the dark theme through Archify's own viewer code, and writes
// .assets/companions/<name>.svg and <name>-dark.svg.
//
// Each export gains a band above the diagram with the KTL brand block and the
// diagram's title. It loses the background grid that Archify's SVG export
// keeps by mistake. Its connector labels are set in bold, which grows no label
// because the font is monospaced. It opens 25 per cent larger where Archify
// draws connector labels at 8 px, and it carries Archify's MIT notice.
//
// A maintainer runs it by hand when a figure's subject changes, and commits the
// result. No workflow runs it, and no skill calls Archify. Archify's own
// receipts hold local paths, so they stay in a temporary folder that is removed
// afterwards.
//
// Usage: node scripts/companion-diagrams.mjs [--archify <dir>] [<name>...]
//   <name>     a candidate's name without .archify.json; default: every one
//   --archify  the archify skill's folder; default $ARCHIFY_HOME, else
//              ~/.agents/skills/archify
// Needs Node 18 or later and Chrome or Chromium; ARCHIFY_CHROME names one.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ASSETS = path.join(ROOT, '.assets');
const COMPANIONS = path.join(ASSETS, 'companions');
const BAND = 44;
// Archify draws connector labels at 8 px in these modes and at 10 or 11 px in
// a lifecycle or a sequence; the larger size lifts an 8 px label to 10 px.
const SCALE = { architecture: 1.25, workflow: 1.25, dataflow: 1.25, lifecycle: 1, sequence: 1 };
const INK = { light: '#2C2C2A', dark: '#E6E4DC' };
const CANVAS = { light: '#E4E1D7', dark: '#1C1C1A' };

class Stop extends Error {}

function usage() {
  return 'usage: node scripts/companion-diagrams.mjs [--archify <dir>] [<name>...]';
}

function parse(args) {
  let archify = process.env.ARCHIFY_HOME || path.join(os.homedir(), '.agents', 'skills', 'archify');
  const names = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--archify' && i + 1 < args.length) archify = args[++i];
    else if (args[i] === '-h' || args[i] === '--help') { console.log(usage()); process.exit(0); }
    else if (args[i].startsWith('-')) throw new Stop(`unknown option: ${args[i]}\n${usage()}`);
    else names.push(args[i]);
  }
  return { archify: path.resolve(archify), names };
}

function escapeXml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// The brand block every hand-made figure carries, light and dark, from the
// first figure in .assets/ that has one and a -dark partner.
function brandBlocks() {
  const marker = /<!-- ktl-brand:start -->[\s\S]*?<!-- ktl-brand:end -->/;
  for (const file of fs.readdirSync(ASSETS).sort()) {
    if (!file.endsWith('.svg') || file.endsWith('-dark.svg') || /card|logo/.test(file)) continue;
    const dark = path.join(ASSETS, file.replace(/\.svg$/, '-dark.svg'));
    if (!fs.existsSync(dark)) continue;
    const light = fs.readFileSync(path.join(ASSETS, file), 'utf8').match(marker);
    const night = fs.readFileSync(dark, 'utf8').match(marker);
    if (light && night) return { light: light[0], dark: night[0] };
  }
  throw new Stop('no figure in .assets/ carries the KTL brand block with a -dark partner');
}

function mitNotice(license) {
  const text = fs.readFileSync(license, 'utf8').trim().replace(/--/g, '- -');
  return `<!-- Drawn with Archify, https://github.com/tt-a1i/archify\n\n${text}\n-->`;
}

function finalize({ cli, work, name, type, quality }) {
  try {
    execFileSync(process.execPath, [cli, 'finalize', type, `${name}.json`, `${name}.html`, '--repo-root', ROOT, '--quality', quality, '--json'], {
      cwd: work,
      env: { ...process.env, ARCHIFY_UPDATE_CHECK_DISABLED: '1' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } catch (error) {
    let summary = `${error.stdout || ''}`.trim() || error.message;
    try {
      const receipt = JSON.parse(summary);
      summary = `${receipt.failedStage || receipt.status}: ${(receipt.diagnostics || []).map((d) => `${d.code} ${d.message}`).join('; ')}`;
    } catch { /* not JSON: keep the raw output */ }
    throw new Stop(`${name}: archify finalize failed (${summary})`);
  }
}

// Exports through the viewer's Export menu code: the Blob it hands to
// URL.createObjectURL is the file the menu would download.
async function exportSvg(browser, html) {
  const sid = await browser.sessionPromise;
  const url = pathToFileURL(html);
  url.searchParams.set('theme', 'light');
  const loaded = browser.cdp.waitFor('Page.loadEventFired', sid, 30000);
  loaded.catch(() => {});
  const navigation = await browser.cdp.send('Page.navigate', { url: url.href }, sid);
  if (navigation.errorText) throw new Stop(`could not open ${html}: ${navigation.errorText}`);
  await loaded;
  const result = {};
  for (const [theme, format] of [['light', 'svg-light'], ['dark', 'svg-dark']]) {
    const expression = `(async () => {
      window.alert = function () {};
      if (document.fonts && document.fonts.ready) await document.fonts.ready.catch(() => {});
      if (window.Archify && Archify.layoutStability && Archify.layoutStability.whenStable) await Archify.layoutStability.whenStable();
      document.documentElement.removeAttribute('data-last-export-error');
      let captured = null;
      const original = URL.createObjectURL;
      URL.createObjectURL = function (blob) { captured = blob; return original.call(URL, blob); };
      try { await Archify.exportMenu.run(${JSON.stringify(format)}); } finally { URL.createObjectURL = original; }
      const error = document.documentElement.getAttribute('data-last-export-error');
      if (error) return { error };
      if (!captured) return { error: 'the export produced no file' };
      return { text: await captured.text() };
    })()`;
    const response = await browser.cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }, sid, 60000);
    if (response.exceptionDetails) throw new Stop(`${format} export failed: ${response.exceptionDetails.text}`);
    if (response.result.value.error) throw new Stop(`${format} export failed: ${response.result.value.error}`);
    result[theme] = response.result.value.text;
  }
  return result;
}

function finish(exported, { theme, title, scale, brand, notice }) {
  const prolog = exported.match(/^<\?xml[^>]*\?>\s*/)?.[0] ?? '';
  const svg = exported.slice(prolog.length);
  const open = svg.match(/^<svg\b[^>]*>/);
  if (!open) throw new Stop('the export does not start with <svg>');
  const box = open[0].match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
  if (!box) throw new Stop('the export has no viewBox at the origin');
  const [width, height] = [Number(box[1]), Number(box[2])];
  const total = height + BAND;
  const [shownWidth, shownHeight] = [Math.round(width * scale), Math.round(total * scale)];
  const root = open[0]
    .replace(box[0], `viewBox="0 -${BAND} ${box[1]} ${total}"`)
    .replace(/ width="[\d.]+"/, ` width="${shownWidth}"`)
    .replace(/ height="[\d.]+"/, ` height="${shownHeight}"`)
    .replace(/ width: [\d.]+px; height: [\d.]+px;/, ` width: ${shownWidth}px; height: ${shownHeight}px;`);

  let body = svg.slice(open[0].length);
  const background = body.match(new RegExp(`<rect x="0" y="0" width="${box[1]}" height="${box[2]}" fill="(#[0-9a-fA-F]{6})"/>`));
  if (!background) throw new Stop('the export has no background rectangle');
  const paper = background[1];
  const grid = '<rect width="100%" height="100%" fill="url(#grid)"/>';
  body = body.replace(grid, '');

  // Centre the title, unless it would run into the brand block on the left.
  const titleWidth = title.length * 9.5;
  const centred = (width - titleWidth) / 2 >= 140;
  const band = [
    `<rect x="0" y="-${BAND}" width="${box[1]}" height="${total}" fill="${paper}"/>`,
    `<g transform="translate(0,-${BAND})">${brand[theme].replace(`stroke="${CANVAS[theme]}"`, `stroke="${paper}"`)}</g>`,
    `<text x="${centred ? width / 2 : 140}" y="${30 - BAND}"${centred ? ' text-anchor="middle"' : ''} font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="${INK[theme]}">${escapeXml(title)}</text>`,
  ].join('');
  body = body.replace(background[0], band);

  const style = '<style>svg .c-grid { stroke: transparent; } svg text[class*="t-edge-"] { font-weight: 700; }</style>';
  return `${prolog}${root}\n${notice}\n${style}${body}${body.endsWith('\n') ? '' : '\n'}`;
}

async function main() {
  const { archify, names } = parse(process.argv.slice(2));
  const cli = path.join(archify, 'bin', 'archify.mjs');
  if (!fs.existsSync(cli)) throw new Stop(`no archify skill at ${archify}; pass --archify <dir> or set ARCHIFY_HOME`);
  const { findChrome, ChromeVisualBrowser } = await import(pathToFileURL(path.join(archify, 'bin', 'visual-check.mjs')).href);
  const chrome = findChrome();
  if (!chrome) throw new Stop('no Chrome or Chromium found; name one in ARCHIFY_CHROME');
  if (names.length === 0) {
    for (const file of fs.readdirSync(COMPANIONS)) if (file.endsWith('.archify.json')) names.push(file.slice(0, -'.archify.json'.length));
    names.sort();
  }
  if (names.length === 0) throw new Stop('no .assets/companions/*.archify.json to render');

  const brand = brandBlocks();
  const notice = mitNotice(path.join(archify, 'LICENSE'));
  const work = fs.mkdtempSync(path.join(os.tmpdir(), 'companion-diagrams-'));
  let browser;
  try {
    for (const name of names) {
      const source = path.join(COMPANIONS, `${name}.archify.json`);
      if (!fs.existsSync(source)) throw new Stop(`no ${path.relative(ROOT, source)}`);
      const candidate = JSON.parse(fs.readFileSync(source, 'utf8'));
      const type = candidate.diagram_type;
      candidate.meta.output = `${name}.html`;
      fs.writeFileSync(path.join(work, `${name}.json`), JSON.stringify(candidate, null, 2));
      finalize({ cli, work, name, type, quality: candidate.meta.quality_profile || 'showcase' });
      if (!browser) {
        browser = new ChromeVisualBrowser(chrome);
        try { await browser.cdp.send('Browser.setDownloadBehavior', { behavior: 'deny' }); } catch { /* older Chrome */ }
        await browser.cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false }, await browser.sessionPromise);
      }
      const exported = await exportSvg(browser, path.join(work, `${name}.html`));
      for (const theme of ['light', 'dark']) {
        const out = path.join(COMPANIONS, theme === 'light' ? `${name}.svg` : `${name}-dark.svg`);
        const text = finish(exported[theme], { theme, title: candidate.meta.title, scale: SCALE[type] ?? 1, brand, notice });
        fs.writeFileSync(out, text);
        console.log(`${path.relative(ROOT, out)}\t${Buffer.byteLength(text)} bytes`);
      }
    }
  } finally {
    if (browser) {
      browser.close();
      if (typeof browser.finishClose === 'function') await browser.finishClose();
    }
    fs.rmSync(work, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(`companion-diagrams: ${error instanceof Stop ? error.message : error.stack}`);
  process.exitCode = 1;
});
