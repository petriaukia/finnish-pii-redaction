"""CLI-entrypoint: aja 3 moodia (Privacy Filter / regex / hybrid) datasetilla.

Tallettaa raa'at spanit results/<iter>/ -hakemistoon ja kirjoittaa reports/iteration_<iter>.md.

    python scripts/eval.py --data data/iteration_0_smoke.jsonl --iter 0 [--device mps|cpu]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import run_privacy_filter as pf  # noqa: E402
import run_regex_baseline as rx  # noqa: E402
import run_hybrid as hy  # noqa: E402
import evaluate_spans as ev  # noqa: E402
import report  # noqa: E402


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _save(path: Path, results: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="Privacy Filter -evaluointi, 3 moodia")
    p.add_argument("--data", required=True)
    p.add_argument("--iter", required=True, help="Iteraation tunnus, esim. 0")
    p.add_argument("--device", choices=["mps", "cuda", "cpu"], default=None)
    args = p.parse_args()

    rows = _read_jsonl(Path(args.data))
    print(f"[eval] {len(rows)} esimerkkia, iteraatio {args.iter}", file=sys.stderr)

    pf_res = pf.run_dataset(rows, args.device)
    rx_res = rx.run_dataset(rows)
    hy_res = hy.run_dataset(rows, args.device)

    rdir = ROOT / "results" / f"iteration_{args.iter}"
    _save(rdir / "privacy_filter.jsonl", pf_res)
    _save(rdir / "regex.jsonl", rx_res)
    _save(rdir / "hybrid.jsonl", hy_res)

    runs = {
        "Privacy Filter only": ev.evaluate_run(rows, {r["id"]: r["spans"] for r in pf_res}),
        "Regex only": ev.evaluate_run(rows, {r["id"]: r["spans"] for r in rx_res}),
        "Hybrid": ev.evaluate_run(rows, {r["id"]: r["spans"] for r in hy_res}),
    }

    md = report.build(args.iter, len(rows), runs)
    rep = ROOT / "reports" / f"iteration_{args.iter}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text(md, encoding="utf-8")
    print(f"[eval] raportti: {rep}", file=sys.stderr)

    # Tilannekuvaa varten: tallenna iteraation totals koneluettavasti.
    metrics = {"iter": args.iter, "size": len(rows),
               "runs": {name: e["totals"] for name, e in runs.items()}}
    (rdir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2),
                                       encoding="utf-8")

    for name, e in runs.items():
        t = e["totals"]
        tr = t["typed_recall"] and round(t["typed_recall"] * 100)
        rr = t["redaction_recall"] and round(t["redaction_recall"] * 100)
        print(f"  {name:22} typed={tr}%  maskaus={rr}%  vuodot={t['n_leaks']}  FP={t['n_false_positives']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
