"""Throughput-benchmarkin puhtaat apufunktiot (chunkkaus + lapaisymatematiikka).

Itse ajastus ei ole yksikkotestattavissa deterministisesti; nama apurit ovat.
"""
import benchmark as bm


def test_throughput_mb_per_second_math():
    r = bm.throughput(1_000_000, 2.0)
    assert r["mb_per_s"] == 0.5
    assert r["bytes"] == 1_000_000
    assert r["seconds"] == 2.0


def test_throughput_zero_seconds_is_safe():
    # Ei saa kaatua nollajakoon.
    r = bm.throughput(1000, 0.0)
    assert r["mb_per_s"] is None


def test_estimate_seconds_for_target_mb():
    assert bm.estimate_seconds(mb_per_s=0.5, target_mb=1.0) == 2.0


def test_chunk_text_respects_max_chars():
    text = " ".join(["sana"] * 1000)  # ~5000 merkkia
    chunks = bm.chunk_text(text, max_chars=100)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)
    assert all(c.strip() for c in chunks)


def test_chunk_text_preserves_content():
    text = "Matti Virtanen asuu Mannerheimintie 12 Helsingissa ja maksaa laskut ajoissa"
    chunks = bm.chunk_text(text, max_chars=20)
    assert " ".join(chunks).split() == text.split()


def test_chunk_text_short_text_single_chunk():
    text = "lyhyt teksti"
    assert bm.chunk_text(text, max_chars=100) == [text]
