#!/usr/bin/env python3
"""
Generate a professional stacked bar chart of RTC/WebRTC CVEs per year
and macro-area.

Input:  evaluation/processed/nvd_relevant_cves.csv
Output: evaluation/outputs/yearly_plane_distribution.png  (matplotlib)
        evaluation/outputs/yearly_plane_distribution.svg  (always)

The chart is completely general: it derives all counts directly from the
classified CSV and does not rely on REPRESENTATIVE_SCENARIOS or any other
paper-specific constant.
"""

from __future__ import annotations

import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT          = Path(__file__).resolve().parents[2]
EVAL_DIR      = ROOT / "evaluation"
PROCESSED_DIR = EVAL_DIR / "processed"
OUTPUTS_DIR   = EVAL_DIR / "outputs"

PLANE_ORDER = [
    "Relay / Traversal",
    "Signaling / Parser",
    "Media / Transport",
    "Web / Backend / API",
    "Client / Browser",
]

COLORS = {
    "Relay / Traversal":   "#2c7fb8",
    "Signaling / Parser":  "#7fcdbb",
    "Media / Transport":   "#f03b20",
    "Web / Backend / API": "#fd8d3c",
    "Client / Browser":    "#756bb1",
}

def load_relevant_cves(path: Path) -> list[dict]:
    if not path.exists():
        print(f"ERROR: input file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def build_matrix(
    rows: list[dict],
) -> tuple[list[int], dict[str, list[int]], list[int]]:
    counts: dict[int, Counter] = defaultdict(Counter)
    for row in rows:
        try:
            year = int(row["year"])
        except (KeyError, ValueError):
            continue
        plane = row.get("macro_area", "")
        if plane in PLANE_ORDER:
            counts[year][plane] += 1

    years = sorted(counts.keys())
    matrix = {
        plane: [counts[y].get(plane, 0) for y in years]
        for plane in PLANE_ORDER
    }
    totals = [
        sum(matrix[plane][i] for plane in PLANE_ORDER)
        for i in range(len(years))
    ]
    return years, matrix, totals


def _chart_mpl(
    years: list[int],
    matrix: dict[str, list[int]],
    totals: list[int],
) -> None:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib.ticker as ticker

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")

    x       = list(range(len(years)))
    bar_w   = 0.62
    bottoms = [0.0] * len(years)

    for plane in PLANE_ORDER:
        values = matrix[plane]
        ax.bar(
            x, values, bottom=bottoms,
            color=COLORS[plane], label=plane,
            width=bar_w, linewidth=0,
        )
        bottoms = [b + v for b, v in zip(bottoms, values)]

    for i, total in enumerate(totals):
        if total > 0:
            ax.text(
                i, total + max(totals) * 0.012,
                str(total),
                ha="center", va="bottom",
                fontsize=8.5, color="#333333",
            )

    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years], fontsize=10)
    ax.set_ylabel("CVE count", fontsize=10, labelpad=8)
    ax.set_xlabel("Year", fontsize=10, labelpad=8)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=6))
    ax.set_ylim(0, max(totals) * 1.15 if totals else 10)

    ax.yaxis.grid(True, linestyle="--", linewidth=0.5,
                  color="#CCCCCC", alpha=0.7)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_linewidth(0.6)
        ax.spines[spine].set_color("#AAAAAA")

    ax.set_title(
        "RTC/WebRTC CVEs per year by macro-area  \u00b7  NVD 2016\u20132026",
        fontsize=12, fontweight="normal", color="#222222", pad=14,
    )

    legend_patches = [
        mpatches.Patch(facecolor=COLORS[p], label=p, linewidth=0)
        for p in PLANE_ORDER
    ]
    ax.legend(
        handles=legend_patches,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.13),
        ncol=len(PLANE_ORDER),
        fontsize=8.5,
        frameon=False,
        handlelength=1.2,
        handleheight=0.9,
        columnspacing=1.4,
    )

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = OUTPUTS_DIR / "yearly_plane_distribution.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"PNG saved: {out}", file=sys.stderr)


def _chart_svg(
    years: list[int],
    matrix: dict[str, list[int]],
    totals: list[int],
) -> None:
    width        = 1080
    height       = 480
    left         = 56
    right_margin = 16
    top          = 72
    bottom       = 56
    chart_w      = width - left - right_margin
    chart_h      = height - top - bottom

    max_total = max(totals) if totals else 10
    scale_max = math.ceil(max_total / 10.0) * 10.0
    n         = len(years)
    bar_gap   = 12
    bar_w     = (chart_w - bar_gap * (n - 1)) / max(n, 1)

    def y_top(value: float) -> float:
        return top + chart_h - (value / scale_max * chart_h)

    p: list[str] = []

    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    p.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
    p.append(
        f'<rect x="{left}" y="{top}" '
        f'width="{chart_w}" height="{chart_h}" fill="#FAFAFA"/>'
    )

    p.append("<style>")
    p.append(
        "text { font-family: -apple-system, Arial, sans-serif; fill: #222222; }"
    )
    p.append(".title { font-size: 14px; font-weight: 400; fill: #222222; }")
    p.append(".axis  { stroke: #AAAAAA; stroke-width: 0.8; fill: none; }")
    p.append(
        ".grid  { stroke: #CCCCCC; stroke-width: 0.6; "
        "stroke-dasharray: 4 4; fill: none; }"
    )
    p.append(".tick  { font-size: 11px; fill: #555555; }")
    p.append(".total { font-size: 10px; fill: #333333; }")
    p.append(".ylabel{ font-size: 11px; fill: #555555; }")
    p.append(".leg   { font-size: 10.5px; fill: #333333; }")
    p.append("</style>")

    p.append(
        f'<text class="title" '
        f'x="{left + chart_w / 2:.1f}" y="20" '
        f'text-anchor="middle">'
        f'RTC/WebRTC CVEs per year by macro-area'
        f'\u2002\u00b7\u2002NVD 2016\u20132026'
        f'</text>'
    )

    leg_swatch   = 11
    leg_gap      = 22
    leg_text_pad = 15
    leg_total_w  = sum(
        leg_swatch + leg_text_pad + len(plane) * 6.2 + leg_gap
        for plane in PLANE_ORDER
    ) - leg_gap
    lx = (width - leg_total_w) / 2
    ly = 34

    for plane in PLANE_ORDER:
        p.append(
            f'<rect x="{lx:.1f}" y="{ly}" '
            f'width="{leg_swatch}" height="{leg_swatch}" '
            f'fill="{COLORS[plane]}" rx="2"/>'
        )
        p.append(
            f'<text class="leg" '
            f'x="{lx + leg_swatch + 4:.1f}" '
            f'y="{ly + 9:.1f}">{plane}</text>'
        )
        lx += leg_swatch + leg_text_pad + len(plane) * 6.2 + leg_gap

    p.append(
        f'<text class="ylabel" '
        f'x="{-(top + chart_h / 2):.1f}" y="14" '
        f'text-anchor="middle" '
        f'transform="rotate(-90)">CVE count</text>'
    )

    tick_count = 5
    for i in range(tick_count + 1):
        val = scale_max * i / tick_count
        y   = y_top(val)
        p.append(
            f'<line class="grid" '
            f'x1="{left}" y1="{y:.1f}" '
            f'x2="{left + chart_w}" y2="{y:.1f}"/>'
        )
        p.append(
            f'<text class="tick" '
            f'x="{left - 8}" y="{y + 4:.1f}" '
            f'text-anchor="end">{val:.0f}</text>'
        )

    for i, year in enumerate(years):
        x          = left + i * (bar_w + bar_gap)
        bottom_val = 0.0

        for plane in PLANE_ORDER:
            val = matrix[plane][i]
            if val == 0:
                bottom_val += val
                continue
            y_b   = y_top(bottom_val)
            y_t   = y_top(bottom_val + val)
            seg_h = y_b - y_t

            p.append(
                f'<rect x="{x:.1f}" y="{y_t:.1f}" '
                f'width="{bar_w:.1f}" height="{seg_h:.1f}" '
                f'fill="{COLORS[plane]}"/>'
            )
            bottom_val += val

        if totals[i] > 0:
            p.append(
                f'<text class="total" '
                f'x="{x + bar_w / 2:.1f}" '
                f'y="{y_top(totals[i]) - 5:.1f}" '
                f'text-anchor="middle">{totals[i]}</text>'
            )

        p.append(
            f'<text class="tick" '
            f'x="{x + bar_w / 2:.1f}" '
            f'y="{top + chart_h + 18:.1f}" '
            f'text-anchor="middle">{year}</text>'
        )

    p.append(
        f'<line class="axis" '
        f'x1="{left}" y1="{top}" '
        f'x2="{left}" y2="{top + chart_h}"/>'
    )
    p.append(
        f'<line class="axis" '
        f'x1="{left}" y1="{top + chart_h}" '
        f'x2="{left + chart_w}" y2="{top + chart_h}"/>'
    )

    p.append("</svg>")

    out = OUTPUTS_DIR / "yearly_plane_distribution.svg"
    out.write_text("\n".join(p), encoding="utf-8")
    print(f"SVG saved: {out}", file=sys.stderr)


def generate_yearly_chart(
    year_plane_subcat: dict[int, dict[str, Counter]],
) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    years = sorted(year_plane_subcat.keys())
    matrix = {
        plane: [
            sum(year_plane_subcat[y].get(plane, Counter()).values())
            for y in years
        ]
        for plane in PLANE_ORDER
    }
    totals = [
        sum(matrix[plane][i] for plane in PLANE_ORDER)
        for i in range(len(years))
    ]
    _render(years, matrix, totals)


def _render(
    years: list[int],
    matrix: dict[str, list[int]],
    totals: list[int],
) -> None:
    try:
        _chart_mpl(years, matrix, totals)
    except Exception as exc:
        print(f"matplotlib unavailable ({exc}), skipping PNG.", file=sys.stderr)
        _chart_svg(years, matrix, totals)


def main() -> int:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_relevant_cves(PROCESSED_DIR / "nvd_relevant_cves.csv")
    years, matrix, totals = build_matrix(rows)
    if not years:
        print("No classifiable rows found in CSV.", file=sys.stderr)
        return 1
    _render(years, matrix, totals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())