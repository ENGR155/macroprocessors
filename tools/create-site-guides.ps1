# Regenerate the thin Quarto entry points without duplicating canonical Markdown.
$ErrorActionPreference = 'Stop'
$siteRoot = Split-Path -Parent $PSScriptRoot
Get-ChildItem -LiteralPath (Join-Path $siteRoot 'docs') -Filter '*.md' | ForEach-Object {
    $text = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
    $title = (($text -split "`n")[0] -replace '^#\s+', '').Trim()
    $yamlTitle = $title.Replace("'", "''")
    $content = "---`ntitle: '$yamlTitle'`nbody-classes: guide-page`n---`n`n[Documentation](../documentation.qmd) / Technical guide`n`n{{< include $($_.Name) >}}`n"
    [IO.File]::WriteAllText((Join-Path $_.DirectoryName ($_.BaseName + '.qmd')), $content, [Text.UTF8Encoding]::new($false))
}
