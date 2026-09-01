#!/usr/bin/env python3
"""Generate experience timeline SVG with terminal styling."""

from __future__ import annotations

import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "experience.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def traffic_dots(cx_start: int, cy: int) -> str:
    return "".join(
        f'<circle cx="{cx_start + i * 20}" cy="{cy}" r="6" fill="{c}"/>'
        for i, c in enumerate(DOT_COLORS)
    )


def build_svg(profile: dict) -> str:
    exp_list = profile["experience"]
    PAD_LEFT = 40
    TIMELINE_X = PAD_LEFT + 12

    elements: list[str] = []
    y = 90
    t = 0.2

    start_y = y

    for entry in exp_list:
        company = entry["company"]
        role = entry["role"]
        duration = entry["duration"]
        highlights = entry.get("highlights", [])
        techs = entry.get("technologies", [])

        # Timeline node circle
        elements.append(
            f'<circle cx="{TIMELINE_X}" cy="{y}" r="6" fill="#3fb950" stroke="#010409" stroke-width="2"/>'
        )

        # Role & Company Header
        header_text = f'{role} @ {company}'
        elements.append(
            f'<text x="{TIMELINE_X + 22}" y="{y + 5}" class="role-title" opacity="0">{esc(header_text)}'
            f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.15s" from="0" to="1" fill="freeze"/></text>'
        )

        # Duration right-aligned
        elements.append(
            f'<text x="836" y="{y + 5}" class="duration" text-anchor="end" opacity="0">{esc(duration)}'
            f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.15s" from="0" to="1" fill="freeze"/></text>'
        )
        t += 0.1
        y += 26

        # Bullet highlights (wrapped)
        for h in highlights:
            lines = textwrap.wrap(h, width=82)
            for i, line in enumerate(lines):
                bullet = "• " if i == 0 else "  "
                elements.append(
                    f'<text x="{TIMELINE_X + 22}" y="{y}" class="bullet" opacity="0">{esc(bullet + line)}'
                    f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.12s" from="0" to="1" fill="freeze"/></text>'
                )
                y += 20
            t += 0.05
        y += 6

        # Tech tags
        if techs:
            tech_str = "  ·  ".join(techs)
            elements.append(
                f'<text x="{TIMELINE_X + 22}" y="{y}" class="tech-tag" opacity="0">{esc(tech_str)}'
                f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.12s" from="0" to="1" fill="freeze"/></text>'
            )
            y += 26

        y += 28

    end_y = y - 36
    # Connecting line behind nodes
    connecting_line = (
        f'<line x1="{TIMELINE_X}" y1="{start_y}" x2="{TIMELINE_X}" y2="{end_y}" '
        f'stroke="#21262d" stroke-width="2"/>'
    )

    height = y + 20
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Experience timeline">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <text x="{PAD_LEFT}" y="62" class="prompt">$ cat experience.log</text>
  <style>
    .prompt     {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .role-title {{ font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #e6edf3; font-weight: 700; }}
    .duration   {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #3fb950; }}
    .bullet     {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #8b949e; }}
    .tech-tag   {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #3fb950; opacity: 0.85; }}
  </style>
  {connecting_line}
  {''.join(elements)}
</svg>'''


def build_single_exp_card(entry: dict) -> str:
    """Render a standalone experience card SVG with hover styling for HTML <a> wrapping."""
    company = entry["company"]
    role = entry["role"]
    duration = entry["duration"]
    highlights = entry.get("highlights", [])
    techs = entry.get("technologies", [])

    CARD_W = 900
    INNER_W = 864
    PAD_LEFT = 32
    TIMELINE_X = PAD_LEFT + 12

    elements: list[str] = []
    y = 32

    # Timeline circle
    elements.append(
        f'<circle cx="{TIMELINE_X}" cy="{y}" r="6" fill="#3fb950" stroke="#010409" stroke-width="2"/>'
    )

    # Header & Duration
    header_text = f'{role} @ {company}'
    elements.append(
        f'<text x="{TIMELINE_X + 22}" y="{y + 5}" class="role-title">{esc(header_text)}</text>'
    )
    elements.append(
        f'<text x="{INNER_W - PAD_LEFT - 120}" y="{y + 5}" class="duration" text-anchor="end">{esc(duration)}</text>'
    )
    elements.append(
        f'<text x="{INNER_W - PAD_LEFT}" y="{y + 5}" class="arrow" text-anchor="end">View ↗</text>'
    )
    y += 26

    # Highlights
    for h in highlights:
        lines = textwrap.wrap(h, width=82)
        for i, line in enumerate(lines):
            bullet = "• " if i == 0 else "  "
            elements.append(
                f'<text x="{TIMELINE_X + 22}" y="{y}" class="bullet">{esc(bullet + line)}</text>'
            )
            y += 20
        y += 4
    y += 6

    # Tech tags
    if techs:
        tech_str = "  ·  ".join(techs)
        elements.append(
            f'<text x="{TIMELINE_X + 22}" y="{y}" class="tech-tag">{esc(tech_str)}</text>'
        )
        y += 24

    card_height = y + 20

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{card_height}" viewBox="0 0 {CARD_W} {card_height}" role="img" aria-label="{esc(company)} experience card">
  <rect width="100%" height="100%" fill="#0d1117" rx="12"/>
  <g class="card-group">
    <rect x="18" y="10" width="{INNER_W}" height="{card_height - 20}" rx="10" class="card-bg"/>
    <g transform="translate(18, 10)">
      {''.join(elements)}
    </g>
  </g>
  <style>
    .card-bg   {{ fill: #010409; stroke: #21262d; stroke-width: 1.5; transition: all 0.2s ease; }}
    .role-title {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; fill: #e6edf3; font-weight: 700; }}
    .duration   {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #3fb950; }}
    .arrow      {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #7d8590; transition: fill 0.2s ease; }}
    .bullet     {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #8b949e; }}
    .tech-tag   {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #3fb950; opacity: 0.85; }}
    svg:hover .card-bg {{ stroke: #3fb950; fill: #0d1117; }}
    svg:hover .arrow   {{ fill: #3fb950; }}
  </style>
</svg>'''


def main() -> None:
    profile = load_profile()
    OUTPUT_PATH.write_text(build_svg(profile), encoding="utf-8")

    # Generate individual experience cards
    for idx, entry in enumerate(profile["experience"], 1):
        card_path = ROOT / "assets" / f"card-exp-{idx}.svg"
        card_path.write_text(build_single_exp_card(entry), encoding="utf-8")


if __name__ == "__main__":
    main()

