// Validate rendered local links/assets, including in-page fragment targets.
// Run after `quarto render`: node tools/check-site.mjs
import { readdir, readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../_site/', import.meta.url));
const pages = [];
const unpublishedFolders = new Set(['build', 'cad', 'graphify-out', '.git', '.quarto', '.venv', '.uv-cache', 'node_modules', '__pycache__']);
async function collect(folder) {
  for (const entry of await readdir(folder, { withFileTypes: true })) {
    if (entry.isDirectory() && unpublishedFolders.has(entry.name)) {
      throw new Error(`Unexpected local-only directory in site output: ${path.relative(root, path.join(folder, entry.name))}`);
    }
    if (['site_libs', 'assets', 'firmware', 'fpga', 'tests', 'tools', 'hardware', 'data'].includes(entry.name)) continue;
    const target = path.join(folder, entry.name);
    if (entry.isDirectory()) await collect(target);
    else if (entry.name.endsWith('.html')) pages.push(target);
  }
}
await collect(root);
if (!pages.length) throw new Error('No rendered HTML pages found; run quarto render before checking the site.');
const content = new Map(await Promise.all(pages.map(async p => [p, await readFile(p, 'utf8')])));
const issues = [];
let checked = 0;
for (const [page, html] of content) {
  for (const match of html.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
    const value = match[1].replace(/&amp;/g, '&');
    if (/^(?:[a-z][\w+.-]*:|\/\/)/i.test(value) || value === '#') continue;
    const url = new URL(value, 'https://local.invalid/' + path.relative(root, page).replaceAll('\\', '/'));
    const target = path.join(root, decodeURIComponent(url.pathname));
    try {
      const info = await stat(target);
      if (info.isDirectory()) continue;
      checked++;
      if (url.hash && content.has(target)) {
        const id = decodeURIComponent(url.hash.slice(1));
        const escaped = id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        if (!new RegExp('\\bid="' + escaped + '"').test(content.get(target))) {
          issues.push(`${path.relative(root, page)}: missing anchor ${value}`);
        }
      }
    } catch {
      issues.push(`${path.relative(root, page)}: missing resource ${value}`);
    }
  }
}
if (issues.length) { console.error(issues.join('\n')); process.exitCode = 1; }
else console.log(`PASS: ${pages.length} pages; ${checked} local links and assets; all fragment targets exist.`);
