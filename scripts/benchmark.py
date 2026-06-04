"""Suorituskyky-benchmark: kuinka kauan Privacy Filter kayttaa esim. 1 MB tekstia,
ja paljonko se vie muistia talla koneella.

Palvelun kannalta ratkaiseva: jos malli on liian hidas tai muistisyoppo, sen arvo
romahtaa riippumatta tarkkuudesta.

Apufunktiot (chunk_text, throughput, estimate_seconds) ovat puhtaita ja testattuja.
Ajastus ja muisti mitataan main():ssa.

CLI:
    python scripts/benchmark.py --mb 1.0
    python scripts/benchmark.py --mb 1.0 --chunk-chars 2000 --device mps
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


# --- Puhtaat apufunktiot (testattu) ---

def throughput(n_bytes: int, seconds: float) -> dict:
    mb = n_bytes / 1_000_000
    return {
        "bytes": n_bytes,
        "mb": mb,
        "seconds": seconds,
        "mb_per_s": (mb / seconds) if seconds > 0 else None,
    }


def estimate_seconds(mb_per_s: float, target_mb: float) -> float:
    return target_mb / mb_per_s


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Pilko teksti enintaan max_chars-mittaisiin paloihin sanarajoilla."""
    words = text.split()
    chunks: list[str] = []
    cur = ""
    for w in words:
        cand = w if not cur else f"{cur} {w}"
        if len(cand) > max_chars and cur:
            chunks.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        chunks.append(cur)
    return chunks


# --- Korpuksen rakennus ja muisti ---

def build_corpus(target_mb: float) -> str:
    """Rakenna ~target_mb edustavaa suomenkielista tekstia testidatasta toistamalla."""
    import json as _json

    texts = []
    for p in sorted((ROOT / "data").glob("*.jsonl")):
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                texts.append(_json.loads(ln)["text"])
    base = " ".join(texts) + " "
    target_bytes = int(target_mb * 1_000_000)
    reps = max(1, target_bytes // len(base.encode("utf-8")) + 1)
    return (base * reps)[: target_bytes // 1]  # likimain target, merkkitarkkuus riittaa


def _peak_rss_mb() -> float:
    # macOS: ru_maxrss tavuina; Linux: kilotavuina.
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss / (1024 * 1024) if sys.platform == "darwin" else rss / 1024


def main() -> int:
    p = argparse.ArgumentParser(description="Privacy Filter -lapaisykyky ja muisti")
    p.add_argument("--mb", type=float, default=1.0, help="Korpuksen koko megatavuina")
    p.add_argument("--chunk-chars", type=int, default=2000, help="Palan enimmaiskoko merkkeina")
    p.add_argument("--device", choices=["mps", "cuda", "cpu"], default=None)
    args = p.parse_args()

    import run_privacy_filter as pf

    rss_before = _peak_rss_mb()
    t_load0 = time.perf_counter()
    pf.get_pipeline(args.device)
    load_s = time.perf_counter() - t_load0
    rss_after_load = _peak_rss_mb()

    text = build_corpus(args.mb)
    n_bytes = len(text.encode("utf-8"))
    chunks = chunk_text(text, args.chunk_chars)

    # Warmup yhdella palalla (ei mukaan ajastukseen).
    pf.detect(chunks[0], args.device)

    t0 = time.perf_counter()
    n_spans = 0
    for c in chunks:
        n_spans += len(pf.detect(c, args.device))
    elapsed = time.perf_counter() - t0

    tp = throughput(n_bytes, elapsed)
    peak_rss = _peak_rss_mb()

    result = {
        "device": pf._device() if args.device is None else args.device,
        "corpus_mb": round(tp["mb"], 3),
        "chunks": len(chunks),
        "chunk_chars": args.chunk_chars,
        "spans_found": n_spans,
        "model_load_s": round(load_s, 2),
        "process_s": round(elapsed, 2),
        "mb_per_s": round(tp["mb_per_s"], 4) if tp["mb_per_s"] else None,
        "est_s_per_1mb": round(estimate_seconds(tp["mb_per_s"], 1.0), 2) if tp["mb_per_s"] else None,
        "model_rss_mb": round(rss_after_load - rss_before, 1),
        "peak_rss_mb": round(peak_rss, 1),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

    out = ROOT / "results" / "benchmark.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[benchmark] {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
