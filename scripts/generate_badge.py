#!/usr/bin/env python3
"""Generate a coverage badge SVG from JSON coverage data.

Usage:
    python3 scripts/generate_badge.py <coverage_json_path> <output_svg_path> [--backend]

--backend: expects pytest-cov JSON format (data['totals']['percent_covered'])
default: expects istanbul JSON-summary format (data['total']['lines']['pct'])
"""

import json
import sys


def make_badge(pct: float) -> str:
    if pct >= 90:
        color = "#4c1"
    elif pct >= 70:
        color = "#97ca00"
    elif pct >= 50:
        color = "#dfb317"
    elif pct >= 30:
        color = "#fe7d37"
    else:
        color = "#e05d44"

    label_pct = f"{pct:.0f}%"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="130" height="20">'
        f'<rect width="90" height="20" fill="#555" rx="3"/>'
        f'<rect x="90" width="40" height="20" fill="{color}" rx="3"/>'
        f'<text x="45" y="14" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" '
        f'font-size="11" fill="#fff" text-anchor="middle">coverage</text>'
        f'<text x="110" y="14" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" '
        f'font-size="11" fill="#fff" text-anchor="middle">{label_pct}</text>'
        f"</svg>"
    )


def main():
    json_path = sys.argv[1]
    output_path = sys.argv[2]
    is_backend = "--backend" in sys.argv

    with open(json_path) as f:
        data = json.load(f)

    if is_backend:
        pct = data["totals"]["percent_covered"]
    else:
        pct = data["total"]["lines"]["pct"]

    svg = make_badge(float(pct))

    with open(output_path, "w") as f:
        f.write(svg)

    print(f"Generated {output_path} with {pct:.1f}% coverage")


if __name__ == "__main__":
    main()
