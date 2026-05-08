#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'trading' / 'performance-sleeve.json'
OUT = ROOT / 'market-briefings' / 'performance' / 'index.html'


def money(x: float) -> str:
    return f"${x:,.2f}"


def pct(x: float) -> str:
    return f"{x:.2f}%"


def pts(x: float) -> str:
    return f"{x:.2f} pts"


def open_position_row(p: dict) -> str:
    pl_text = p.get('pl_text', money(p.get('pl', 0)))
    weight_text = p.get('weight_text', pct(p.get('weight_pct', 0)))
    return (
        f"          <tr><td>{p['ticker']}</td><td>{p.get('status','Open')}</td>"
        f"<td>{p.get('entry_date','-')}</td><td>{money(p.get('cost_basis',0))}</td>"
        f"<td>{money(p.get('current_value',0))}</td><td>{pl_text}</td><td>{weight_text}</td></tr>"
    )


def closed_trade_row(t: dict) -> str:
    return_text = t.get('return_text', pct(t.get('return_pct', 0)))
    return (
        f"          <tr><td>{t['ticker']}</td><td>{t.get('opened','-')}</td><td>{t.get('closed','-')}</td>"
        f"<td>{t.get('entry','-')}</td><td>{t.get('exit','-')}</td><td>{return_text}</td><td>{t.get('reason','-')}</td></tr>"
    )


def main() -> int:
    data = json.loads(DATA.read_text())
    start_date = data.get('start_date') or 'Begins with first executed project-sleeve trade'
    status = data.get('status', 'unknown').replace('-', ' ').title()
    open_positions = data.get('open_positions', [])
    closed_trades = data.get('closed_trades', [])

    open_rows = '\n'.join(open_position_row(p) for p in open_positions) or '          <tr><td colspan="7">No project-sleeve positions yet.</td></tr>'
    closed_rows = '\n'.join(closed_trade_row(t) for t in closed_trades) or '          <tr><td colspan="7">No closed project-sleeve trades yet.</td></tr>'
    notes = '\n'.join(f'        <li>{n}</li>' for n in data.get('notes', []))

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>$5,000 Sleeve Performance Tracker — Carve Market Desk</title>
  <link rel="stylesheet" href="../styles.css" />
</head>
<body>
  <header class="site-header site-nav">
    <div class="wrap">
      <nav class="nav-bar" aria-label="Primary">
        <a class="nav-link" href="../index.html">Research & Briefings</a>
        <a class="nav-link" href="../recommendations/index.html">Trade Recommendations</a>
        <a class="nav-link nav-link-active" href="index.html">Portfolio Performance</a>
      </nav>
    </div>
  </header>
  <main class="wrap report-shell">
    <p><a href="../index.html">← Back to Market Desk</a></p>

    <header class="report-header card">
      <p class="kicker">Carve Market Desk</p>
      <h1>$5,000 Sleeve Performance Tracker</h1>
      <p class="meta">Dedicated scorecard for the separate project sleeve inside Public account {data['account']}</p>
      <p class="summary">This page tracks only Tyler's dedicated $5,000 trading sleeve. It does not use the full Public.com account as the performance base.</p>
    </header>

    <section class="card">
      <h2 class="section-title">Scoreboard</h2>
      <div class="metric-grid">
        <article class="metric-card"><p class="detail-label">Starting Capital</p><h3>{money(data['starting_capital'])}</h3></article>
        <article class="metric-card"><p class="detail-label">Current Value</p><h3>{money(data['current_value'])}</h3></article>
        <article class="metric-card"><p class="detail-label">Current Cash</p><h3>{money(data['current_cash'])}</h3></article>
        <article class="metric-card"><p class="detail-label">Net Return</p><h3>{pct(data['net_return_pct'])}</h3></article>
        <article class="metric-card"><p class="detail-label">S&amp;P 500 Benchmark</p><h3>{pct(data['benchmark']['return_pct'])}</h3></article>
        <article class="metric-card"><p class="detail-label">Relative Performance</p><h3>{pts(data['benchmark']['relative_performance_pts'])}</h3></article>
        <article class="metric-card"><p class="detail-label">Max Drawdown</p><h3>{pct(data['max_drawdown_pct'])}</h3></article>
        <article class="metric-card"><p class="detail-label">Status</p><h3>{status}</h3></article>
      </div>
    </section>

    <section class="card">
      <h2 class="section-title">Mandate Status</h2>
      <div class="detail-grid">
        <div><p class="detail-label">Tracking Scope</p><p>Separate $5,000 sleeve only</p></div>
        <div><p class="detail-label">Start Date</p><p>{start_date}</p></div>
        <div><p class="detail-label">Benchmark Rule</p><p>{data['benchmark']['rule']}</p></div>
        <div><p class="detail-label">Portfolio Shape</p><p>{data['mandate']['portfolio_shape']}</p></div>
        <div><p class="detail-label">Allowed Scope</p><p>{data['mandate']['allowed_scope']}</p></div>
        <div><p class="detail-label">BITB Cap</p><p>{data['mandate']['bitb_cap_pct']}%</p></div>
      </div>
    </section>

    <section class="card">
      <h2 class="section-title">Open Positions</h2>
      <table class="tracker-table"><thead><tr><th>Ticker</th><th>Status</th><th>Entry Date</th><th>Cost Basis</th><th>Current Value</th><th>P/L</th><th>Weight</th></tr></thead><tbody>
{open_rows}
      </tbody></table>
    </section>

    <section class="card">
      <h2 class="section-title">Closed Trades</h2>
      <table class="tracker-table"><thead><tr><th>Ticker</th><th>Opened</th><th>Closed</th><th>Entry</th><th>Exit</th><th>Return</th><th>Reason</th></tr></thead><tbody>
{closed_rows}
      </tbody></table>
    </section>

    <section class="card">
      <h2 class="section-title">Tracking Method</h2>
      <ul class="bullet-list">
{notes}
        <li>Last updated: {data['last_updated']}</li>
      </ul>
    </section>
  </main>
</body>
</html>
'''
    OUT.write_text(html)
    print(f"Rendered {OUT}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
