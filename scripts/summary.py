"""Tilannekuva: kokoaa iteraatioiden metriikat yhdeksi vertailunakymaksi.

Syote: lista iteraatiodicteja muotoa
    {"iter": "1", "size": 51, "runs": {
        "Privacy Filter only": {"typed_recall":..,"redaction_recall":..,"n_leaks":..},
        "Regex only": {...},
        "Hybrid": {...}}}

eval.py kirjoittaa jokaiselle iteraatiolle results/iteration_<n>/metrics.json talla
rakenteella; summary lukee ne ja tuottaa reports/summary.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _pct(x) -> str:
    return "-" if x is None else f"{x * 100:.0f} %"


def iteration_overview(iterations: list[dict]) -> list[dict]:
    """Poimi kustakin iteraatiosta vertailun avainluvut (yksi rivi per iteraatio)."""
    rows = []
    for it in iterations:
        pf = it["runs"]["Privacy Filter only"]
        hy = it["runs"]["Hybrid"]
        rows.append({
            "iter": it["iter"],
            "size": it["size"],
            "pf_redaction": pf["redaction_recall"],
            "pf_leaks": pf["n_leaks"],
            "hybrid_typed": hy["typed_recall"],
            "hybrid_redaction": hy["redaction_recall"],
            "hybrid_leaks": hy["n_leaks"],
        })
    return rows


def build_summary(iterations: list[dict]) -> str:
    rows = iteration_overview(iterations)
    out = [
        "# Tilannekuva - Privacy Filter vs. regex vs. hybrid (suomi)",
        "",
        "Vertailu iteraatioittain. **Maskaus** = maskattiinko PII lainkaan (vuotosuoja);",
        "**tyypitetty** = oikealla tyypilla (taksonomian laatu); **vuodot** = PII jai kokonaan lapi.",
        "",
        "| Iteraatio | Esimerkkeja | Malli yksin (maskaus) | Malli yksin (vuodot) | Hybrid (tyypitetty) | Hybrid (maskaus) | Hybrid (vuodot) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        out.append(
            f"| {r['iter']} | {r['size']} | {_pct(r['pf_redaction'])} | {r['pf_leaks']} | "
            f"{_pct(r['hybrid_typed'])} | {_pct(r['hybrid_redaction'])} | {r['hybrid_leaks']} |"
        )
    out += [
        "",
        "## Tulkinta",
        "",
        "- Malli yksin jattaa formaaleja suomalaisia tunnisteita lapi ja ylimaskaa suomea.",
        "- Hybridi (saannot formaaleihin + malli vapaaseen tekstiin) sulkee vuodot lahes nollaan.",
        "- Maskaus != anonymisointi: epasuora tunnistettavuus jaa (ks. iteraatio 3).",
        "",
    ]
    return "\n".join(out)


def _load_metrics(iters: list[str]) -> list[dict]:
    data = []
    for n in iters:
        p = ROOT / "results" / f"iteration_{n}" / "metrics.json"
        if p.exists():
            data.append(json.loads(p.read_text(encoding="utf-8")))
    return data


def main() -> int:
    p = argparse.ArgumentParser(description="Kokoa iteraatioiden tilannekuva")
    p.add_argument("--iters", nargs="+", required=True, help="Iteraatiotunnukset, esim. 0 1 2")
    args = p.parse_args()
    iterations = _load_metrics(args.iters)
    md = build_summary(iterations)
    out = ROOT / "reports" / "summary.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"[summary] {out} ({len(iterations)} iteraatiota)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
