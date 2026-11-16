# E155 Magnetic Levitation — Quarto website

The website uses a basic Quarto report layout, similar to the E155 course website
and Carlos and Maynor's project site. The writing follows the authors' E155 lab
reports: explain the design, describe the tests, and state what remains to be done.
Top-level pages are authored in `.qmd`; technical guides include the existing
engineering Markdown files.

## Build and preview

From the repository root with Quarto on PATH:

```powershell
quarto render
node tools/check-site.mjs
quarto preview --no-browser
```

Open the local URL printed by Quarto. Rendered output is in `_site/` (ignored by Git).
The site uses relative resource URLs and can be hosted beneath a GitHub Pages
repository path. No hosting configuration or publication is performed automatically.

## Publishing

After a successful render and link check, run `quarto publish gh-pages` to update
the existing GitHub Pages publication.

Resource and render globs in `_quarto.yml` start with `/` to anchor them to the
project root. Quarto otherwise searches recursively: `tests/**` and `assets/**`
also match folders inside local CAD/Python dependencies. Publishing those caches
can fail on Windows with `Filename too long`. Keep the leading slashes when
editing the lists. The site checker rejects local-only output folders and an
empty render.

If a previous failed publish left caches in `_site` or a
`.quarto/quarto-publish-worktree-*` folder, remove only those generated folders
before rendering again. Source CAD files and the CAD environment stay in place.

## Edit the site

| File | Content |
|---|---|
| `index.qmd` | Introduction, project status, documentation links, and authors |
| `progress.qmd` | November 15 progress report, CAD iterations, bench tests, current diagrams and schematics |
| `design.qmd`, `mcu.qmd`, `fpga.qmd` | Architecture and separate implementation pages |
| `hardware.qmd` | Assembled components, latest wiring, and remaining characterization |
| `documentation.qmd` | Guide directory, course deliverables, source downloads |
| `results.qmd` | Current bench observations, earlier software evidence, and pending measurements |
| `about.qmd`, `ai.qmd`, `references.qmd` | Project information, disclosure, credits |
| `docs/*.md` | Canonical engineering notes; included by matching `.qmd` entry points |
| `assets/theme.scss`, `assets/site.css` | Cosmo theme settings and small reading/accessibility adjustments |
| `assets/site.js` | Accessible mobile toggle and scrollable technical tables |
| `assets/progress-report/` | Published copies of CAD images and the midpoint diagrams/schematic downloads |

Edit the Markdown notes to update existing detailed guides. For a new note, run
`./tools/create-site-guides.ps1` to generate its Quarto entry point, then add a link
from `documentation.qmd`. The link filter in `assets/doc-links.lua` maps known
engineering Markdown links to their HTML pages; extend its guide-name list when
adding a new guide with links from other notes.

Mermaid blocks use Quarto's `{mermaid}` fence syntax so they render as diagrams.
The previous concept illustration and its generator remain in the repository but
are not displayed on the current site.

## Design and verification

Layout and writing references are credited in
`references.qmd`. No React runtime, paid component assets, external fonts, or remote
image assets are required. Quarto supplies its local search and diagram scripts;
mathematical expressions use native MathML, without a remote rendering library.

`tools/check-site.mjs` checks rendered local links, fragment identifiers, and assets.
Browser review should additionally cover mobile/desktop layouts, the navigation
menu, search, source-file links, table scrolling, reduced motion,
and diagram rendering. Local QA screenshots and temporary browser scripts belong
under the ignored `outputs/` directory.

Hardware results, team contribution details, schematics, photos, and demonstration video
must be added from actual project evidence before this is presented as a completed
hardware report. The results page explicitly attributes engineering checks to the
October 26, 2026 verification record for the earlier application, and separates it from the revised design and later SPI bring-up.
