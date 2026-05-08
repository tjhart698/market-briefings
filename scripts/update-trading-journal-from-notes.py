#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

if len(sys.argv) != 4:
    raise SystemExit("Usage: update-trading-journal-from-notes.py <date> <notes-json> <workspace-root>")

date_str = sys.argv[1]
notes = json.loads(Path(sys.argv[2]).read_text())
root = Path(sys.argv[3]).resolve()
log_path = root / 'trading' / 'journal-log.md'
report_path = root / 'market-briefings' / 'reports' / f'{date_str}-trading-journal.html'

fields = {
    'Trades taken or considered': notes.get('trades', 'not provided yet'),
    'Why entered / why not entered': notes.get('why', 'not provided yet'),
    'Daily P/L': notes.get('pl', 'not provided yet'),
    'Mistakes made': notes.get('mistakes', 'not provided yet'),
    'Lessons for tomorrow': notes.get('lessons', 'not provided yet'),
}

section = ['### ' + date_str]
for k, v in fields.items():
    section.append(f'- {k}: {v}')
section_text = '\n'.join(section)

if log_path.exists():
    text = log_path.read_text()
else:
    text = '# Trading Journal Log\n\n'

import re
pat = re.compile(rf"### {re.escape(date_str)}\n(?:- .*\n?)+(?:\n---\n)?", re.M)
if pat.search(text):
    text = pat.sub(section_text + '\n\n---\n', text, count=1)
else:
    if not text.endswith('\n'):
        text += '\n'
    text += '\n' + section_text + '\n\n---\n'
log_path.write_text(text)

if report_path.exists():
    report = report_path.read_text()
    block = '<section class="card">\n      <h2 class="section-title">Closeout Journal</h2>\n      <ul class="bullet-list">\n'
    for k, v in fields.items():
        block += f'        <li><strong>{k}:</strong> {v}</li>\n'
    block += '      </ul>\n    </section>'
    if 'Awaiting Tyler\'s closeout journal input.' in report:
        report = report.replace('<section class="card">\n      <h2 class="section-title">Status</h2>\n      <p>Awaiting Tyler\'s closeout journal input.</p>\n    </section>', block)
    elif '<h2 class="section-title">Closeout Journal</h2>' in report:
        report = re.sub(r'<section class="card">\s*<h2 class="section-title">Closeout Journal</h2>[\s\S]*?</section>', block, report, count=1)
    else:
        report = report.replace('<section class="card">\n      <h2>Bottom Line</h2>', block + '\n\n    <section class="card">\n      <h2>Bottom Line</h2>', 1)
    report_path.write_text(report)
