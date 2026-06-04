"""Hybrid-ajo: Privacy Filter + regex. Todennakoisin tuotantokandidaatti.

Yhdistaa mallin ja regexin spanit. Paallekkaisissa offset-valeissa regex voittaa
formaaleissa tunnisteissa (sotu/IP/IBAN), koska niiden tarkkuus on regexilla korkeampi.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import run_privacy_filter as pf  # noqa: E402
import run_regex_baseline as rx  # noqa: E402

# Naissa tyypeissa regex on auktoriteetti -> sen span syrjayttaa paallekkaisen mallin spanin.
REGEX_WINS = {"finnish_ssn", "ip", "iban"}


def _overlap(a: dict, b: dict) -> bool:
    if a["start"] is None or b["start"] is None:
        return a["text"] == b["text"]
    return not (a["end"] <= b["start"] or a["start"] >= b["end"])


def merge(model_spans: list[dict], regex_spans: list[dict]) -> list[dict]:
    merged = list(regex_spans)
    for ms in model_spans:
        clash = next((rs for rs in regex_spans if _overlap(ms, rs)), None)
        if clash is None:
            merged.append(ms)
        elif clash["type"] not in REGEX_WINS:
            # ei formaali tunniste -> pidetaan molemmat vain jos eri teksti
            if ms["text"] != clash["text"]:
                merged.append(ms)
    merged.sort(key=lambda x: (x["start"] if x["start"] is not None else 1 << 30))
    return merged


def run_dataset(rows: list[dict], device: str | None = None) -> list[dict]:
    model = {r["id"]: r["spans"] for r in pf.run_dataset(rows, device)}
    regex = {r["id"]: r["spans"] for r in rx.run_dataset(rows)}
    return [{"id": r["id"], "spans": merge(model.get(r["id"], []), regex.get(r["id"], []))} for r in rows]


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="Hybrid (Privacy Filter + regex)")
    p.add_argument("--data", required=True)
    p.add_argument("--device", choices=["mps", "cuda", "cpu"], default=None)
    args = p.parse_args()
    for r in run_dataset(_read_jsonl(Path(args.data)), args.device):
        print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
