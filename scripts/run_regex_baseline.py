"""Regex-baseline: suomalaisiin formaatteihin raataloity saantopohjainen PII-tunnistus.

Testisuunnitelman par. 7. Ensimmainen versio saa olla ylikattava: parempi false positive
kuin sotu lapi. Palauttaa saman span-formaatin offseteineen kuin run_privacy_filter.

CLI:
    python scripts/run_regex_baseline.py --data data/iteration_1_formal_identifiers.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from type_mapping import DEFAULT_CRITICALITY  # noqa: E402

# Henkilotunnus: erotin = vuosisatamerkki, tarkistusmerkki 31-merkkisesta joukosta.
# Erottimet: + (1800), -/Y/X/W/V/U (1900), A-F (2000). Tarkistusmerkki: 0-9 ABCDEFHJKLMNPRSTUVWXY.
SSN = re.compile(r"\b\d{6}[-+ABCDEFYXWVU]\d{3}[0-9ABCDEFHJKLMNPRSTUVWXY]\b")

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")

# IPv6: kattaa taydet ja :: -lyhennetyt muodot (esim. 2001:14bb:180:1234::1).
# Rajaus hex/kaksoispiste-luokilla, jotta virkkeen lopussa oleva piste (esim. "...::1.")
# ei estaisi osumaa.
IPV6 = re.compile(
    r"(?<![0-9A-Fa-f:])(?:"
    r"(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}"
    r"|(?:[0-9A-Fa-f]{1,4}:){1,7}:"
    r"|(?:[0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4}"
    r"|(?:[0-9A-Fa-f]{1,4}:){1,5}(?::[0-9A-Fa-f]{1,4}){1,2}"
    r"|(?:[0-9A-Fa-f]{1,4}:){1,4}(?::[0-9A-Fa-f]{1,4}){1,3}"
    r"|(?:[0-9A-Fa-f]{1,4}:){1,3}(?::[0-9A-Fa-f]{1,4}){1,4}"
    r"|(?:[0-9A-Fa-f]{1,4}:){1,2}(?::[0-9A-Fa-f]{1,4}){1,5}"
    r"|[0-9A-Fa-f]{1,4}:(?::[0-9A-Fa-f]{1,4}){1,6}"
    r"|:(?:(?::[0-9A-Fa-f]{1,4}){1,7}|:)"
    r")(?![0-9A-Fa-f:])"
)

# FI-IBAN: FI + 2 tarkistusnumeroa + 14 numeroa, voi olla ryhmitelty valilyonneilla.
IBAN_FI = re.compile(r"\bFI\d{2}(?:\s?\d){14}\b")

# Suomalainen puhelinnumero: +358- tai 0-alkuinen, valilyonnit/viivat sallittu.
PHONE = re.compile(r"(?<!\d)(?:\+358[\s-]?|0)\d(?:[\s-]?\d){5,9}(?!\d)")

# Valinnainen secret/API-avain (suppea ensiversio).
SECRET = re.compile(r"\b(?:sk|pk|ghp|gho)[-_][A-Za-z0-9]{16,}\b")

PATTERNS = [
    ("finnish_ssn", SSN),
    ("iban", IBAN_FI),
    ("email", EMAIL),
    ("ip", IPV6),
    ("ip", IPV4),
    ("secret", SECRET),
    ("phone", PHONE),
]


def detect(text: str) -> list[dict]:
    """Palauta regex-spanit. Paallekkaiset valit karsitaan (aiempi pattern voittaa)."""
    spans: list[dict] = []
    taken: list[tuple[int, int]] = []
    for ptype, pat in PATTERNS:
        for m in pat.finditer(text):
            s, e = m.start(), m.end()
            if any(not (e <= ts or s >= te) for ts, te in taken):
                continue  # paallekkainen jo loydetyn kanssa
            taken.append((s, e))
            spans.append(
                {
                    "text": m.group(0).strip(),
                    "type": ptype,
                    "criticality": DEFAULT_CRITICALITY.get(ptype, "medium"),
                    "score": 1.0,
                    "start": s,
                    "end": e,
                    "source": "regex",
                }
            )
    spans.sort(key=lambda x: x["start"])
    return spans


def run_dataset(rows: list[dict]) -> list[dict]:
    return [{"id": r["id"], "spans": detect(r["text"])} for r in rows]


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="Regex-baseline (suomalaiset formaatit)")
    p.add_argument("--data", required=True, help="JSONL-datasetti")
    args = p.parse_args()
    for r in run_dataset(_read_jsonl(Path(args.data))):
        print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
