"""Privacy Filter -ajo: OpenAI Privacy Filter token-classification -mallina.

Ei chat-malli. Ajetaan transformers-pipelinella in-process (vrt. tab-triage/benchmarks/
evaluate_baseline.py MLX-polku). Palauttaa spanit natiivisti aggregation_strategy=simple.

CLI:
    python scripts/run_privacy_filter.py --self-test
    python scripts/run_privacy_filter.py --data data/iteration_0_smoke.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from type_mapping import map_model_type, DEFAULT_CRITICALITY  # noqa: E402

MODEL_ID = "openai/privacy-filter"

_PIPELINE = None


def _device() -> str:
    import torch

    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def get_pipeline(device: str | None = None):
    """Lataa pipeline kerran (singleton). Warmup tehdaan kutsujan puolelta."""
    global _PIPELINE
    if _PIPELINE is None:
        from transformers import pipeline

        dev = device or _device()
        print(f"[privacy_filter] lataa {MODEL_ID} ({dev})...", file=sys.stderr, flush=True)
        t0 = time.perf_counter()
        _PIPELINE = pipeline(
            task="token-classification",
            model=MODEL_ID,
            aggregation_strategy="simple",
            device=dev,
        )
        print(f"[privacy_filter] valmis ({time.perf_counter() - t0:.1f}s)", file=sys.stderr, flush=True)
    return _PIPELINE


def _merge_adjacent(raw: list[dict], text: str) -> list[dict]:
    """Yhdista perakkaiset saman tyypin spanit, joiden valissa on vain whitespacea.

    Malli kayttaa BIOES-tageja (B/I/E/S), mutta transformersin "simple"-aggregaatio
    olettaa IOB2:n eika yhdista B...E-rajaa. Tasta "Harry Potter" -> "Harry"+"Potter" ja
    email katkeaa. Offset-pohjainen yhdistys palauttaa kokonaiset spanit.
    """
    if not raw:
        return raw
    raw = sorted(raw, key=lambda e: (e.get("start") or 0))
    merged = [raw[0]]
    for ent in raw[1:]:
        prev = merged[-1]
        gap = text[prev.get("end") or 0:ent.get("start") or 0]
        same = ent["entity_group"] == prev["entity_group"]
        if same and prev.get("end") is not None and ent.get("start") is not None and gap.strip() == "":
            prev["end"] = ent["end"]
            prev["score"] = min(prev["score"], ent["score"])
        else:
            merged.append(ent)
    return merged


def detect(text: str, device: str | None = None) -> list[dict]:
    """Palauta normalisoidut spanit: {text, type, criticality, score, start, end, source}."""
    pipe = get_pipeline(device)
    out = _merge_adjacent([dict(e) for e in pipe(text)], text)
    spans: list[dict] = []
    for ent in out:
        ptype = map_model_type(ent["entity_group"])
        start = int(ent["start"]) if ent.get("start") is not None else None
        end = int(ent["end"]) if ent.get("end") is not None else None
        word = (text[start:end] if start is not None else ent["word"]).strip()
        spans.append(
            {
                "text": word,
                "type": ptype,
                "criticality": DEFAULT_CRITICALITY.get(ptype, "medium"),
                "score": round(float(ent["score"]), 4),
                "start": start,
                "end": end,
                "source": "privacy_filter",
            }
        )
    return spans


def run_dataset(rows: list[dict], device: str | None = None) -> list[dict]:
    """Aja koko datasetti. Warmup ekalla rivilla, jotta latausaika ei vaaristy."""
    if not rows:
        return []
    get_pipeline(device)
    detect(rows[0]["text"], device)  # warmup
    results = []
    for r in rows:
        results.append({"id": r["id"], "spans": detect(r["text"], device)})
    return results


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="OpenAI Privacy Filter -ajo")
    p.add_argument("--self-test", action="store_true", help="Aja yksi englanninkielinen esimerkki ja tulosta spanit")
    p.add_argument("--data", help="JSONL-datasetti")
    p.add_argument("--device", choices=["mps", "cuda", "cpu"], default=None)
    args = p.parse_args()

    if args.self_test:
        text = "My name is Harry Potter and my email is harry.potter@hogwarts.edu."
        print(f"INPUT: {text}")
        for s in detect(text, args.device):
            print(f"  {s['type']:12} score={s['score']:.3f}  {s['text']!r}")
        return 0

    if args.data:
        rows = _read_jsonl(Path(args.data))
        for r in run_dataset(rows, args.device):
            print(json.dumps(r, ensure_ascii=False))
        return 0

    p.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
