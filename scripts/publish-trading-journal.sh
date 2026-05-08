#!/bin/zsh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

DATE_ARG="${1:-$(TZ=America/Chicago date +%F)}"
REPORT_REL="reports/${DATE_ARG}-trading-journal.html"
REPORT_PATH="$REPO_DIR/$REPORT_REL"
TITLE="Trading Journal"
HUMAN_DATE="$(TZ=America/Chicago date -j -f %F "$DATE_ARG" "+%B %-d, %Y")"
SUMMARY="Closeout journal for Tyler's trading project: trades taken or considered, rationale, daily P/L, mistakes, and lessons for tomorrow."
EXCERPT="Daily closeout journal for Tyler's trading project."

mkdir -p "$REPO_DIR/reports"

if [[ ! -f "$REPORT_PATH" ]]; then
  cat >"$REPORT_PATH" <<HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${TITLE} — ${HUMAN_DATE}</title>
  <link rel="stylesheet" href="../styles.css" />
</head>
<body>
  <main class="wrap report-shell">
    <p><a href="../index.html">← Back to archive</a></p>

    <header class="report-header card">
      <p class="kicker">Carve Market Desk</p>
      <h1>${TITLE}</h1>
      <p class="meta">Published ${HUMAN_DATE}</p>
      <p class="summary">${SUMMARY}</p>
    </header>

    <section class="card">
      <h2 class="section-title">Status</h2>
      <p>Awaiting Tyler's closeout journal input.</p>
    </section>

    <section class="card">
      <h2>Bottom Line</h2>
      <p class="footer-note">This page was created by the scheduled closeout workflow and will be updated after Tyler provides the day's trading notes.</p>
      <p class="footer-note">For research and briefing purposes only. Not personalized financial advice.</p>
    </section>
  </main>
</body>
</html>
HTML
fi

python3 - "$REPO_DIR/index.html" "$DATE_ARG" "$REPORT_REL" "$TITLE" "$EXCERPT" <<'PY'
import sys, re
from pathlib import Path
index_path = Path(sys.argv[1])
date_arg, report_rel, title, excerpt = sys.argv[2:6]
text = index_path.read_text()

latest_re = re.compile(r'(<section class="card">\s*<h2>Latest Briefing</h2>\s*<article class="report-row">\s*<div>\s*<p class="report-date">)(.*?)(</p>\s*<h3><a href=")(.*?)(">)(.*?)(</a></h3>\s*<p>)(.*?)(</p>\s*</div>\s*<a class="button" href=")(.*?)(">Open report</a>\s*</article>\s*</section>)', re.S)
new_latest = rf'\g<1>{date_arg}\g<3>{report_rel}\g<5>{title}\g<7>{excerpt}\g<9>{report_rel}\g<10>'
text, count = latest_re.subn(new_latest, text, count=1)
if count != 1:
    raise SystemExit('Could not update Latest Briefing block')

archive_marker = f'<a href="{report_rel}">{title}</a>'
if archive_marker not in text:
    insert_after = '<ul class="archive-list">\n'
    archive_entry = f'''        <li>\n          <span>{date_arg}</span>\n          <a href="{report_rel}">{title}</a>\n        </li>\n'''
    if insert_after not in text:
        raise SystemExit('Could not find archive list insertion point')
    text = text.replace(insert_after, insert_after + archive_entry, 1)

index_path.write_text(text)
PY

if [[ -n "$(git status --porcelain)" ]]; then
  git add index.html "$REPORT_REL"
  git commit -m "Publish trading journal for ${DATE_ARG}"
  git push origin main
else
  echo "No changes to publish."
fi
