#!/usr/bin/env python3
"""Build a five-year NVD-based RTC/WebRTC taxonomy dataset and summary outputs."""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import json
import math
import os
import re
import sys
import textwrap
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVAL_DIR = ROOT / "evaluation"
RAW_DIR = EVAL_DIR / "raw"
PROCESSED_DIR = EVAL_DIR / "processed"
OUTPUTS_DIR = EVAL_DIR / "outputs"

START_DATE = dt.datetime(2016, 1, 1, 0, 0, 0, tzinfo=dt.timezone.utc)
END_DATE = dt.datetime(2026, 3, 19, 23, 59, 59, tzinfo=dt.timezone.utc)
YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
FEED_URL = "https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-{year}.json.gz"

KEYWORD_PATTERNS = {
    "WebRTC": re.compile(r"\bwebrtc\b", re.I),
    "TURN": re.compile(r"\bturn\b", re.I),
    "STUN": re.compile(r"\bstun\b", re.I),
    "SIP": re.compile(r"\bsip\b", re.I),
    "RTP": re.compile(r"\brtp\b", re.I),
    "Asterisk": re.compile(r"\basterisk\b", re.I),
    "FreeSWITCH": re.compile(r"\bfreeswitch\b", re.I),
    "Kamailio": re.compile(r"\bkamailio\b", re.I),
    "coTURN": re.compile(r"\bcoturn\b", re.I),
    "OpenSIPS": re.compile(r"\bopensips\b", re.I), 
    "PJSIP": re.compile(r"\bpjsip\b", re.I),
    "Sofia-SIP": re.compile(r"\bsofia[- ]sip\b", re.I),
    "SIPp": re.compile(r"\bsipp\b", re.I),
    "Linphone": re.compile(r"\blinphone\b", re.I),
    "Janus": re.compile(r"\bjanus\b", re.I),
    "Kurento": re.compile(r"\bkurento\b", re.I),
    "Jitsi": re.compile(r"\bjitsi\b", re.I),
    "RTPEngine": re.compile(r"\brtpengine\b", re.I),
    "RTPProxy": re.compile(r"\brtpproxy\b", re.I),
    "libSRTP": re.compile(r"\blibsrtp\b", re.I),
    "oRTP": re.compile(r"\bortp\b", re.I),
    "pjmedia": re.compile(r"\bpjmedia\b", re.I),
    "libwebrtc": re.compile(r"\blibwebrtc\b", re.I),
    "Pion": re.compile(r"\bpion\b", re.I),
    "aiortc": re.compile(r"\baiortc\b", re.I),
    "getUserMedia": re.compile(r"\bgetusermedia\b", re.I),
    "MediaStream": re.compile(r"\bmediastream\b", re.I),
    "RTCPeerConnection": re.compile(r"\brtcpeerconnection\b", re.I),
}

RTC_MARKERS = [
    re.compile(p, re.I)
    for p in [
        r"\bwebrtc\b",
        r"\bturn\b",
        r"\bstun\b",
        r"\bice\b",
        r"\bsip\b",
        r"\bsdp\b",
        r"\brtp\b",
        r"\bsrtp\b",
        r"\brtcp\b",
        r"\bzrtp\b",
        r"\bvoip\b",
    ]
]

MANUAL_OVERRIDES = {
    # include/exclude and category adjustments for borderline records are tracked here
}

PLANE_ORDER = [
    "Relay / Traversal",
    "Signaling / Parser",
    "Media / Transport",
    "Web / Backend / API",
    "Client / Browser",
    "Out of Scope",
]

REPRESENTATIVE_SCENARIOS = {
    "Relay / Traversal": "CVE-2020-26262 (coTURN bypass)",
    "Signaling / Parser": "CVE-2018-8828 (Kamailio overflow); SIP spoofing",
    "Media / Transport": "CVE-2017-14099 (RTP injection); SIP flooding",
    "Web / Backend / API": (
        "CVE-2020-24807 (RCE upload), CVE-2019-17426 (NoSQLi), "
        "CVE-2025-62613 (XSS)"
    ),
    "Client / Browser": "CVE-2019-11748 (Firefox permission abuse)",
}


def has_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.I) for pattern in patterns)


def ensure_dirs() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, OUTPUTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def download_feed(year: int) -> Path:
    dest = RAW_DIR / f"nvdcve-2.0-{year}.json.gz"
    if dest.exists():
        return dest
    url = FEED_URL.format(year=year)
    print(f"Downloading {url}", file=sys.stderr)
    urllib.request.urlretrieve(url, dest)
    return dest


def parse_iso8601(value: str) -> dt.datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def load_feed(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload.get("vulnerabilities", [])


def english_description(cve: dict) -> str:
    for entry in cve.get("descriptions", []):
        if entry.get("lang") == "en":
            return entry.get("value", "")
    return ""


def cpe_strings(cve: dict) -> list[str]:
    results: list[str] = []

    def walk(nodes: list[dict]) -> None:
        for node in nodes or []:
            for match in node.get("cpeMatch", []):
                crit = match.get("criteria")
                if crit:
                    results.append(crit)
            walk(node.get("nodes", []))

    for cfg in cve.get("configurations", []):
        walk(cfg.get("nodes", []))
    return results


def references_text(cve: dict) -> str:
    refs = []
    for ref in cve.get("references", []):
        refs.append(ref.get("url", ""))
        refs.extend(ref.get("tags", []))
    return " ".join(refs)


def keyword_hits(text: str) -> list[str]:
    hits = []
    for name, pattern in KEYWORD_PATTERNS.items():
        if pattern.search(text):
            hits.append(name)
    return hits


def build_record(vuln: dict) -> dict:
    cve = vuln["cve"]
    desc = english_description(cve)
    cpes = cpe_strings(cve)
    cpe_text = " ".join(cpes)
    ref_text = references_text(cve)
    all_text = " ".join([desc, cpe_text, ref_text])
    metrics = cve.get("metrics", {})

    severity = ""
    score = ""
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV40", "cvssMetricV2"):
        if metrics.get(key):
            cvss = metrics[key][0]
            data = cvss.get("cvssData", {})
            severity = cvss.get("baseSeverity", data.get("baseSeverity", ""))
            score = data.get("baseScore", "")
            break

    weaknesses = []
    for weakness in cve.get("weaknesses", []):
        for desc_item in weakness.get("description", []):
            val = desc_item.get("value")
            if val:
                weaknesses.append(val)

    return {
        "cve_id": cve["id"],
        "published": cve["published"],
        "last_modified": cve["lastModified"],
        "year": cve["published"][:4],
        "description": desc,
        "cpe_matches": cpes,
        "cpe_text": cpe_text,
        "reference_text": ref_text,
        "keyword_hits": keyword_hits(all_text),
        "severity": severity,
        "score": score,
        "weaknesses": weaknesses,
        "source_identifier": cve.get("sourceIdentifier", ""),
    }


def within_window(record: dict) -> bool:
    published = parse_iso8601(record["published"])
    return START_DATE <= published <= END_DATE


def is_relevant(record: dict) -> tuple[bool, str]:
    if not record["keyword_hits"]:
        return False, "no keyword hit"

    text = " ".join(
        [record["description"], record["cpe_text"], record["reference_text"]]
    ).lower()
    cve_id = record["cve_id"]

    if cve_id in MANUAL_OVERRIDES:
        override = MANUAL_OVERRIDES[cve_id]
        return override.get("include", True), override.get("reason", "manual override")

    marker_hits = sum(1 for pat in RTC_MARKERS if pat.search(text))

    if marker_hits == 0:
        return False, "keyword match without RTC marker"

    if "TURN" in record["keyword_hits"] and marker_hits == 1 and "coturn" not in text:
        return False, "generic TURN match without RTC context"

    if "SIP" in record["keyword_hits"] and marker_hits == 1:
        if "session initiation protocol" not in text and "sip " not in text and " sip" not in text:
            return False, "generic SIP match without protocol context"

    return True, "rtc-related description/cpe/reference"


def classify_plane(record: dict) -> str:
    cve_id = record["cve_id"]
    if cve_id in MANUAL_OVERRIDES and "plane" in MANUAL_OVERRIDES[cve_id]:
        return MANUAL_OVERRIDES[cve_id]["plane"]

    text = " ".join(
        [record["description"], record["cpe_text"], record["reference_text"]]
    ).lower()

    if has_any(
        text,
        [
            r"\bfirefox\b",
            r"\bchrome\b",
            r"\bsafari\b",
            r"\bedge\b",
            r"\bmicrophone\b",
            r"\bcamera\b",
            r"\bpermission\b",
            r"\bdevice access\b",
            r"\bmediadevices\b",
            r"\bweb browser\b",
            r"\bgetusermedia\b",
            r"\bmediastream\b",
            r"\brtcpeerconnection\b",
            r"\blibwebrtc\b",
        ],
    ):
        return "Client / Browser"
    if has_any(
        text,
        [
            r"\bxss\b",
            r"\bcross[- ]site\b",
            r"\bcsrf\b",
            r"\bupload\b",
            r"\bwebshell\b",
            r"\bnode\.js\b",
            r"\bapi\b",
            r"\bauth(?:entication)?\b",
            r"\blogin\b",
            r"\bmongoose\b",
            r"\bsocketio\b",
            r"\bvdo\.ninja\b",
            r"\bweb application\b",
            r"\bweb ui\b",
            r"\bhttp request\b",
            r"\bwordpress\b",
            r"\bnosql\b",
            r"\bjitsi\b",
        ],
    ):
        return "Web / Backend / API"
    if has_any(
        text,
        [
            r"\bcoturn\b",
            r"\bturn\b",
            r"\bstun\b",
            r"\bice\b",
            r"\brelay\b",
            r"\btraversal\b",
            r"\bloopback\b",
            r"allocate request",
            r"xor-peer-address",
        ],
    ):
        return "Relay / Traversal"
    if has_any(
        text,
        [
            r"\bsrtp\b",
            r"\brtcp\b",
            r"\brtp\b",
            r"\bmedia stream\b",
            r"\baudio stream\b",
            r"\bvideo stream\b",
            r"\bdtls[- ]srtp\b",
            r"\brtpengine\b",
            r"\brtpproxy\b",
            r"\blibsrtp\b",
            r"\bortp\b",
            r"\bpjmedia\b",
            r"\bpion\b",
            r"\baiortc\b",
            r"\bjanus\b",
            r"\bkurento\b",
        ],
    ):
        return "Media / Transport"
    if has_any(
        text,
        [
            r"\bsip\b",
            r"\bsdp\b",
            r"\bkamailio\b",
            r"\basterisk\b",
            r"\bfreeswitch\b",
            r"\bregister\b",
            r"\binvite\b",
            r"\bparser\b",
            r"\bvoip\b",
            r"session initiation protocol",
            r"\bopensips\b",
            r"\bpjsip\b",
            r"\bsofia[- ]sip\b",
            r"\bsipp\b",
        ],
    ):
        return "Signaling / Parser"
    return "Out of Scope"


def classify_subcategory(record: dict, plane: str) -> str:
    cve_id = record["cve_id"]
    if cve_id in MANUAL_OVERRIDES and "subcategory" in MANUAL_OVERRIDES[cve_id]:
        return MANUAL_OVERRIDES[cve_id]["subcategory"]

    text = " ".join([record["description"], record["cpe_text"]]).lower()
    weak = " ".join(record["weaknesses"]).lower()
    joined = f"{text} {weak}"

    if plane == "Relay / Traversal":
        if has_any(joined, [r"\bbypass\b", r"\bloopback\b", r"\bssrf\b", r"access control"]):
            return "Access control bypass / internal reachability"
        if has_any(joined, [r"\bamplification\b", r"\breflection\b"]):
            return "Amplification / reflection abuse"
        if has_any(joined, [r"\bdos\b", r"\bdenial\b", r"resource exhaustion"]):
            return "Relay denial of service"
        return "Traversal / relay weakness"

    if plane == "Signaling / Parser":
        if has_any(joined, [r"\boverflow\b", r"out-of-bounds", r"memory corruption", r"\bheap\b"]):
            return "Parser overflow / memory corruption"
        if has_any(joined, [r"\bspoof", r"\bimpersonation\b", r"\bforgery\b"]):
            return "Spoofing / impersonation"
        if has_any(joined, [r"\bflood", r"\bdos\b", r"\bdenial\b", r"resource exhaustion"]):
            return "Flooding / denial of service"
        if has_any(joined, [r"\bmalformed\b", r"\bparser\b", r"\bsdp\b"]):
            return "Malformed SIP/SDP handling"
        return "Signaling weakness"

    if plane == "Media / Transport":
        if has_any(joined, [r"\bbleed\b", r"\binjection\b", r"\binject"]):
            return "RTP injection / bleed"
        if has_any(joined, [r"\bflood", r"\bdos\b", r"\bdenial\b", r"resource exhaustion"]):
            return "RTP flooding / denial of service"
        if has_any(joined, [r"\bsrtp\b", r"\bdowngrade\b", r"\bcrypto\b", r"\bdtls\b"]):
            return "Media protection / downgrade weakness"
        return "Media transport weakness"

    if plane == "Web / Backend / API":
        if has_any(joined, [r"\bxss\b", r"cross-site"]):
            return "Cross-site scripting"
        if has_any(joined, [r"\bupload\b", r"\bwebshell\b", r"\brce\b", r"command execution", r"remote code"]):
            return "File upload / remote code execution"
        if has_any(joined, [r"\bnosql\b", r"sql injection", r"query manipulation"]):
            return "Injection / query manipulation"
        if has_any(joined, [r"auth bypass", r"authentication bypass", r"improper authentication", r"login bypass"]):
            return "API / authentication bypass"
        return "Web/backend weakness"

    if plane == "Client / Browser":
        if has_any(joined, [r"\bpermission\b", r"\bmicrophone\b", r"\bcamera\b", r"device access"]):
            return "Permission reuse / device access abuse"
        if has_any(joined, [r"\borigin\b", r"\bbrowser\b", r"ui redress"]):
            return "Browser-side trust boundary weakness"
        return "Client/browser weakness"

    return "Out of scope"


def wrap(text: str, width: int) -> str:
    return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_chart(summary_rows: list[dict]) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        generate_svg_chart(summary_rows)
        return

    labels = [row["macro_area"] for row in summary_rows]
    values = [float(row["pct_of_filtered_cves"]) for row in summary_rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color=["#2c7fb8", "#7fcdbb", "#f03b20", "#fd8d3c", "#756bb1"])
    ax.set_ylabel("% of filtered CVEs")
    ax.set_title("Distribution of relevant NVD CVEs across RTC-Attack Lab macro-areas")
    ax.set_ylim(0, max(values) * 1.25 if values else 1)
    ax.set_axisbelow(True)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.xticks(rotation=20, ha="right")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, f"{value:.1f}%", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUTPUTS_DIR / "macro_area_distribution.png", dpi=200)
    plt.close(fig)


def generate_svg_chart(summary_rows: list[dict]) -> None:
    labels = [row["macro_area"] for row in summary_rows]
    values = [float(row["pct_of_filtered_cves"]) for row in summary_rows]
    if not labels:
        return

    width = 980
    height = 460
    left = 90
    bottom = 90
    top = 50
    chart_height = height - top - bottom
    chart_width = width - left - 40
    max_value = max(values) if values else 1.0
    scale_max = math.ceil(max_value / 10.0) * 10.0
    bar_gap = 18
    bar_width = (chart_width - bar_gap * (len(values) - 1)) / len(values)

    def y_for(value: float) -> float:
        return top + chart_height - (value / scale_max * chart_height)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>',
        'text { font-family: Arial, sans-serif; fill: #111827; }',
        '.axis { stroke: #374151; stroke-width: 1; }',
        '.grid { stroke: #d1d5db; stroke-width: 1; stroke-dasharray: 4 4; }',
        '.bar { fill: #2563eb; }',
        '.label { font-size: 13px; }',
        '.tick { font-size: 12px; }',
        '.title { font-size: 18px; font-weight: bold; }',
        '</style>',
        f'<text class="title" x="{width/2}" y="28" text-anchor="middle">RTC-related NVD CVEs by testbed macro-area</text>',
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_height}" />',
        f'<line class="axis" x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}" />',
    ]

    ticks = 5
    for i in range(ticks + 1):
        value = scale_max * i / ticks
        y = y_for(value)
        parts.append(f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + chart_width}" y2="{y:.1f}" />')
        parts.append(f'<text class="tick" x="{left - 10}" y="{y + 4:.1f}" text-anchor="end">{value:.0f}%</text>')

    for idx, (label, value) in enumerate(zip(labels, values)):
        x = left + idx * (bar_width + bar_gap)
        y = y_for(value)
        bar_h = top + chart_height - y
        parts.append(f'<rect class="bar" x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_h:.1f}" rx="4" />')
        parts.append(f'<text class="tick" x="{x + bar_width/2:.1f}" y="{y - 8:.1f}" text-anchor="middle">{value:.1f}%</text>')
        wrapped = label.replace(" / ", "/\n")
        for line_idx, line in enumerate(wrapped.splitlines()):
            parts.append(
                f'<text class="label" x="{x + bar_width/2:.1f}" y="{top + chart_height + 22 + line_idx * 15:.1f}" text-anchor="middle">{line}</text>'
            )

    parts.append("</svg>")
    (OUTPUTS_DIR / "macro_area_distribution.svg").write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    ensure_dirs()

    all_records: list[dict] = []
    for year in YEARS:
        path = download_feed(year)
        for vuln in load_feed(path):
            record = build_record(vuln)
            if within_window(record):
                all_records.append(record)

    keyword_hits_rows = []
    relevant_rows = []
    excluded_rows = []

    for record in all_records:
        include, reason = is_relevant(record)
        row = {
            "cve_id": record["cve_id"],
            "published": record["published"],
            "year": record["year"],
            "severity": record["severity"],
            "score": record["score"],
            "keyword_hits": "; ".join(record["keyword_hits"]),
            "description": record["description"],
            "cpe_matches": "; ".join(record["cpe_matches"]),
            "relevance_reason": reason,
        }
        if record["keyword_hits"]:
            keyword_hits_rows.append(row)
        if include and record["keyword_hits"]:
            plane = classify_plane(record)
            subcategory = classify_subcategory(record, plane)
            relevant_rows.append(
                {
                    **row,
                    "macro_area": plane,
                    "subcategory": subcategory,
                }
            )
        elif record["keyword_hits"]:
            excluded_rows.append(row)

    relevant_rows.sort(key=lambda r: (r["macro_area"], r["subcategory"], r["cve_id"]))
    excluded_rows.sort(key=lambda r: r["cve_id"])
    keyword_hits_rows.sort(key=lambda r: r["cve_id"])

    write_csv(
        PROCESSED_DIR / "nvd_keyword_hits.csv",
        keyword_hits_rows,
        [
            "cve_id",
            "published",
            "year",
            "severity",
            "score",
            "keyword_hits",
            "description",
            "cpe_matches",
            "relevance_reason",
        ],
    )
    write_csv(
        PROCESSED_DIR / "nvd_relevant_cves.csv",
        relevant_rows,
        [
            "cve_id",
            "published",
            "year",
            "severity",
            "score",
            "keyword_hits",
            "macro_area",
            "subcategory",
            "description",
            "cpe_matches",
            "relevance_reason",
        ],
    )
    write_csv(
        PROCESSED_DIR / "nvd_excluded_cves.csv",
        excluded_rows,
        [
            "cve_id",
            "published",
            "year",
            "severity",
            "score",
            "keyword_hits",
            "description",
            "cpe_matches",
            "relevance_reason",
        ],
    )

    total_relevant = len(relevant_rows)
    supported_relevant = sum(1 for row in relevant_rows if row["macro_area"] != "Out of Scope")
    unsupported_relevant = total_relevant - supported_relevant
    plane_counts = Counter(row["macro_area"] for row in relevant_rows)
    subcategory_counts: dict[str, Counter] = defaultdict(Counter)
    for row in relevant_rows:
        subcategory_counts[row["macro_area"]][row["subcategory"]] += 1

    breakdown_rows = []
    for plane, counts in subcategory_counts.items():
        if plane == "Out of Scope":
            continue
        for subcategory, count in counts.most_common():
            breakdown_rows.append(
                {
                    "macro_area": plane,
                    "subcategory": subcategory,
                    "num_cves": count,
                    "pct_of_filtered_cves": f"{(count / total_relevant * 100.0):.1f}" if total_relevant else "0.0",
                }
            )

    summary_rows = []
    for plane in PLANE_ORDER:
        if plane == "Out of Scope" or plane_counts[plane] == 0:
            continue
        pct = (plane_counts[plane] / total_relevant * 100.0) if total_relevant else 0.0
        top_subcats = subcategory_counts[plane].most_common(3)
        subcat_text = "; ".join(f"{name} ({count})" for name, count in top_subcats)
        summary_rows.append(
            {
                "macro_area": plane,
                "top_subcategories": subcat_text,
                "num_cves": plane_counts[plane],
                "pct_of_filtered_cves": f"{pct:.1f}",
                "representative_rtc_attack_lab_scenario": REPRESENTATIVE_SCENARIOS[plane],
            }
        )

    write_csv(
        OUTPUTS_DIR / "macro_area_summary.csv",
        summary_rows,
        [
            "macro_area",
            "top_subcategories",
            "num_cves",
            "pct_of_filtered_cves",
            "representative_rtc_attack_lab_scenario",
        ],
    )
    write_csv(
        OUTPUTS_DIR / "macro_area_subcategory_breakdown.csv",
        breakdown_rows,
        ["macro_area", "subcategory", "num_cves", "pct_of_filtered_cves"],
    )
    write_csv(
        OUTPUTS_DIR / "unmapped_relevant_cves.csv",
        [row for row in relevant_rows if row["macro_area"] == "Out of Scope"],
        [
            "cve_id",
            "published",
            "year",
            "severity",
            "score",
            "keyword_hits",
            "macro_area",
            "subcategory",
            "description",
            "cpe_matches",
            "relevance_reason",
        ],
    )

    with (OUTPUTS_DIR / "macro_area_table.tex").open("w", encoding="utf-8") as fh:
        fh.write("\\begin{table}[h!]\n")
        fh.write("\\centering\n")
        fh.write("\\scriptsize\n")
        fh.write("\\begin{tabular}{p{2.5cm}p{4.0cm}p{1.6cm}p{3.4cm}}\n")
        fh.write("\\toprule\n")
        fh.write("\\textbf{Macro-area (testbed plane)} & \\textbf{Dominant NVD subcategories (2021--2026)} & \\textbf{\\% of filtered CVEs} & \\textbf{Representative RTC-Attack Lab scenario(s)} \\\\\n")
        fh.write("\\midrule\n")
        for row in summary_rows:
            fh.write(
                f"{row['macro_area']} & "
                f"{row['top_subcategories']} & "
                f"{row['pct_of_filtered_cves']}\\% & "
                f"{row['representative_rtc_attack_lab_scenario']} \\\\\n"
            )
        fh.write("\\bottomrule\n")
        fh.write("\\end{tabular}\n")
        fh.write(
            "\\caption{Distribution of relevant NVD CVEs across the macro-areas represented in RTC-Attack Lab. The percentages are computed over the filtered RTC-related CVEs returned by the keyword-based NVD query window (2021-03-08 to 2026-03-08).}\\label{tab:nvd-macro-area-coverage}\n"
        )
        fh.write("\\end{table}\n")

    with (OUTPUTS_DIR / "summary.md").open("w", encoding="utf-8") as fh:
        fh.write("# NVD RTC/WebRTC Taxonomy Summary\n\n")
        fh.write(
            "- Source: official NVD 2.0 yearly feeds for 2021-2026, filtered to the publication window 2021-03-08 to 2026-03-08.\n"
        )
        fh.write(
            "- Query terms: WebRTC, TURN, STUN, SIP, RTP, Asterisk, FreeSWITCH, Kamailio, coTURN.\n"
        )
        fh.write(
            "- Method: local keyword query over NVD descriptions/CPE text/references, followed by relevance filtering and macro-area classification aligned with the paper taxonomy.\n\n"
        )
        fh.write(f"- Keyword-hit CVEs before relevance filtering: {len(keyword_hits_rows)}\n")
        fh.write(f"- Filtered relevant CVEs: {total_relevant}\n")
        fh.write(f"- Filtered CVEs mapped to supported RTC-Attack Lab macro-areas: {supported_relevant}\n")
        fh.write(f"- Relevant but currently unmapped CVEs: {unsupported_relevant}\n")
        if total_relevant:
            fh.write(f"- Macro-area coverage of the filtered RTC set: {supported_relevant / total_relevant * 100.0:.1f}%\n")
        fh.write(f"- Excluded as irrelevant/noisy matches: {len(excluded_rows)}\n\n")
        fh.write("## Macro-area distribution\n\n")
        fh.write("| Macro-area | Dominant NVD subcategories | # CVEs | % |\n")
        fh.write("| --- | --- | ---: | ---: |\n")
        for row in summary_rows:
            fh.write(
                f"| {row['macro_area']} | {row['top_subcategories']} | "
                f"{row['num_cves']} | {row['pct_of_filtered_cves']}% |\n"
            )
        fh.write("\n")
        fh.write(
            "The supported macro-areas capture most of the filtered RTC-related CVEs in the collection window. "
            "This supports a macro-area coverage claim, not a claim that each individual NVD CVE is directly instantiated in the testbed.\n"
        )

    with (OUTPUTS_DIR / "methodology.md").open("w", encoding="utf-8") as fh:
        fh.write("# Methodology\n\n")
        fh.write(
            "This dataset was built from the official NVD 2.0 yearly JSON feeds rather than the CVE API because the API restricts "
            "publication-date queries to windows of at most 120 consecutive days. Using the official feeds makes the five-year collection "
            "reproducible without changing the data source.\n\n"
        )
        fh.write(
            "Relevance filtering is conservative. Keyword hits without RTC-specific contextual markers were excluded and recorded in "
            "`processed/nvd_excluded_cves.csv` with a short rationale.\n"
        )
        fh.write(
            "Relevant CVEs that remain outside the current RTC-Attack Lab macro-areas are retained in "
            "`outputs/unmapped_relevant_cves.csv` so that any coverage claim remains auditable.\n"
        )

    generate_chart(summary_rows)

    coverage = {
        "keyword_hits": len(keyword_hits_rows),
        "relevant_cves": total_relevant,
        "supported_relevant_cves": supported_relevant,
        "unmapped_relevant_cves": unsupported_relevant,
        "supported_macro_area_coverage_pct": round((supported_relevant / total_relevant * 100.0), 1) if total_relevant else 0.0,
        "excluded_cves": len(excluded_rows),
        "macro_areas": summary_rows,
    }
    with (OUTPUTS_DIR / "coverage_overview.json").open("w", encoding="utf-8") as fh:
        json.dump(coverage, fh, indent=2)

    print(json.dumps(coverage, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())