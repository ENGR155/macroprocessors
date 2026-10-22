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

## Edit the site

| File | Content |
|---|---|
| `index.qmd` | Introduction, project status, documentation links, and authors |
| `design.qmd`, `mcu.qmd`, `fpga.qmd` | Architecture and separate implementation pages |
| `hardware.qmd` | Candidate components, wiring links, downloadable BOM |
| `documentation.qmd` | Guide directory, course deliverables, source downloads |
| `results.qmd` | Dated software/HDL evidence and pending physical experiments |
| `about.qmd`, `ai.qmd`, `references.qmd` | Project information, disclosure, credits |
| `docs/*.md` | Canonical engineering notes; included by matching `.qmd` entry points |
| `assets/theme.scss`, `assets/site.css` | Cosmo theme settings and small reading/accessibility adjustments |
| `assets/site.js` | Accessible mobile toggle and scrollable technical tables |

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
existing October 15, 2026 verification record.
