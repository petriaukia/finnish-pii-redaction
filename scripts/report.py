"""Markdown-raportti iteraatiolle (testisuunnitelman par. 8 rakenne).

Kaksi recall-mittaria: typed (oikea tyyppi) ja redaction (maskattu lainkaan). Ks.
evaluate_spans.py:n docstring miksi ne eroavat.
"""
from __future__ import annotations


def _pct(x) -> str:
    return "-" if x is None else f"{x * 100:.0f} %"


def _run_section(name: str, ev: dict) -> list[str]:
    t = ev["totals"]
    lines = [f"### {name}", "",
             f"- Odotettu: {t['n_expected']}  tyypitetty: {t['typed_found']} "
             f"({_pct(t['typed_recall'])})  maskattu: {t['masked_found']} "
             f"({_pct(t['redaction_recall'])})",
             f"- Vuodot (ei maskattu): {t['n_leaks']}  vaara tyyppi: {t['n_mislabeled']}  "
             f"false positives: {t['n_false_positives']}",
             "",
             "| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |",
             "|---|---:|---:|---:|"]
    for typ in sorted(ev["per_type"]):
        b = ev["per_type"][typ]
        lines.append(f"| {typ} | {b['n_expected']} | {_pct(b['typed_recall'])} | {_pct(b['redaction_recall'])} |")
    lines.append("")
    return lines


def _leak_table(runs: dict[str, dict]) -> list[str]:
    lines = ["## Vuodot (PII jai kokonaan maskaamatta)", "",
             "| id | tyyppi | odotettu | kriittisyys | ajo |", "|---|---|---|---|---|"]
    for run_name, ev in runs.items():
        for fn in ev["false_negatives"]:
            lines.append(f"| {fn['id']} | {fn['type']} | {fn['expected']} | "
                         f"{fn.get('criticality','')} | {run_name} |")
    lines.append("")
    return lines


def _mislabel_table(runs: dict[str, dict]) -> list[str]:
    lines = ["## Vaara tyyppi (maskattu, mutta luokiteltu vaarin)", "",
             "| id | odotettu tyyppi | teksti | mallin tyyppi | ajo |", "|---|---|---|---|---|"]
    for run_name, ev in runs.items():
        for m in ev["mislabeled"]:
            lines.append(f"| {m['id']} | {m['type']} | {m['expected']} | {m['got_type']} | {run_name} |")
    lines.append("")
    return lines


def _fp_table(runs: dict[str, dict]) -> list[str]:
    lines = ["## False positives (maskattu turhaan)", "",
             "| id | tyyppi | teksti | ajo |", "|---|---|---|---|"]
    for run_name, ev in runs.items():
        for fp in ev["false_positives"]:
            lines.append(f"| {fp['id']} | {fp['type']} | {fp['produced']} | {run_name} |")
    lines.append("")
    return lines


def build(iteration: str, dataset_size: int, runs: dict[str, dict]) -> str:
    """runs: {'Privacy Filter only': ev, 'Regex only': ev, 'Hybrid': ev}."""
    crit_leaks = [
        f"{r}: {fn['type']} (id {fn['id']}, {fn['expected']})"
        for r, ev in runs.items() for fn in ev["false_negatives"]
        if fn.get("criticality") == "high"
    ]
    out = [f"# Iteraatio {iteration} - tulosraportti", "", "## Yhteenveto", "",
           f"- Aineiston koko: {dataset_size}"]
    for name, ev in runs.items():
        t = ev["totals"]
        out.append(f"- {name}: tyypitetty {_pct(t['typed_recall'])}, "
                   f"maskaus {_pct(t['redaction_recall'])}, vuodot {t['n_leaks']}, "
                   f"FP {t['n_false_positives']}")
    out += ["- Kriittiset vuodot (criticality=high): " + (f"{len(crit_leaks)}" if crit_leaks else "0"), ""]
    if crit_leaks:
        out += ["### Kriittiset vuodot", ""] + [f"- {c}" for c in crit_leaks] + [""]
    out += ["## Ajot per moodi", ""]
    for name, ev in runs.items():
        out += _run_section(name, ev)
    out += _leak_table(runs)
    out += _mislabel_table(runs)
    out += _fp_table(runs)
    out += ["## Paatos", "",
            "- [ ] Jatka seuraavaan iteraatioon",
            "- [ ] Korjaa regex",
            "- [ ] Rajaa kayttotapausta",
            "- [ ] Lisaa manuaalinen tarkistus", ""]
    return "\n".join(out)
