"""Span-arviointi: vertaa tuotettuja spaneja datasetin expected_spans-kenttaan.

Kaksi mittaria, koska ne vastaavat eri kysymyksiin:

- **typed recall**: loytyiko span OIKEALLA tyypilla. Mittaa taksonomian laatua.
  Tama paljastaa esim. ettei Privacy Filter ymmarra sotua/IP:ta (silla ei ole niille
  kategoriaa) -> regex pakollinen. Tama on dokumentin hybridi-teesin ydin.
- **redaction recall**: maskattiinko PII-teksti ylipaataan (milla tahansa tyypilla).
  Mittaa vuotosuojaa: jos malli merkitsi sotun "account_numberiksi", data EI vuoda
  vaikka tyyppi on vaara.

True FN = "leak" = teksti jai kokonaan maskaamatta (redaction miss). Nama ovat oikeat
tietosuojaviat. "Mislabeled" = maskattu mutta vaaralla tyypilla (ei vuoto, mutta
taksonomia pielessa).

Matchaus on ekoilla kierroksilla tekstipohjainen (testisuunnitelman par. 10).
"""
from __future__ import annotations

import re

_WS = re.compile(r"\s+")


def _norm(s: str) -> str:
    return _WS.sub(" ", s).strip().lower()


def _text_match(expected: str, produced: str) -> bool:
    e, p = _norm(expected), _norm(produced)
    if not e or not p:
        return False
    return e == p or e in p or p in e


def evaluate_run(dataset: list[dict], produced: dict[object, list[dict]]) -> dict:
    by_type: dict[str, dict] = {}
    fns: list[dict] = []          # true leaks: ei maskattu lainkaan
    mislabeled: list[dict] = []   # maskattu, mutta vaara tyyppi
    fps: list[dict] = []          # tuotettu span jota mikaan odotettu ei kata

    for row in dataset:
        rid = row["id"]
        exp = row.get("expected_spans", [])
        prod = produced.get(rid, [])
        typed_used = [False] * len(prod)

        for es in exp:
            t = es.get("type", "unknown")
            bt = by_type.setdefault(t, {"n_expected": 0, "typed_found": 0, "masked_found": 0})
            bt["n_expected"] += 1

            typed_idx = next(
                (i for i, ps in enumerate(prod)
                 if not typed_used[i] and ps["type"] == t and _text_match(es["text"], ps["text"])),
                None,
            )
            if typed_idx is not None:
                typed_used[typed_idx] = True
                bt["typed_found"] += 1

            masker = next((ps for ps in prod if _text_match(es["text"], ps["text"])), None)
            if masker is not None:
                bt["masked_found"] += 1
                if typed_idx is None:
                    mislabeled.append({"id": rid, "type": t, "expected": es["text"],
                                       "got_type": masker["type"]})
            else:
                fns.append({"id": rid, "type": t, "expected": es["text"],
                            "criticality": es.get("criticality", "")})

        for ps in prod:
            if not any(_text_match(es["text"], ps["text"]) for es in exp):
                fps.append({"id": rid, "type": ps["type"], "produced": ps["text"],
                            "source": ps.get("source", "")})

    for bt in by_type.values():
        n = bt["n_expected"]
        bt["typed_recall"] = (bt["typed_found"] / n) if n else None
        bt["redaction_recall"] = (bt["masked_found"] / n) if n else None

    total_exp = sum(b["n_expected"] for b in by_type.values())
    total_typed = sum(b["typed_found"] for b in by_type.values())
    total_masked = sum(b["masked_found"] for b in by_type.values())
    return {
        "per_type": by_type,
        "false_negatives": fns,
        "mislabeled": mislabeled,
        "false_positives": fps,
        "totals": {
            "n_expected": total_exp,
            "typed_found": total_typed,
            "masked_found": total_masked,
            "typed_recall": (total_typed / total_exp) if total_exp else None,
            "redaction_recall": (total_masked / total_exp) if total_exp else None,
            "n_leaks": len(fns),
            "n_mislabeled": len(mislabeled),
            "n_false_positives": len(fps),
        },
    }
