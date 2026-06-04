"""Hybrid-yhdistys: regex voittaa formaaleissa tunnisteissa, muuten unioni."""
import run_hybrid as hy


def _span(text, typ, start, end, source):
    return {"text": text, "type": typ, "criticality": "high", "score": 1.0,
            "start": start, "end": end, "source": source}


def test_regex_wins_on_overlapping_ssn():
    # Malli merkitsi sotun vaarin (iban), regex oikein -> regex jaa, mallin span putoaa.
    text = "Tunnus 010101A123N."
    model = [_span("010101A123N", "iban", 7, 18, "privacy_filter")]
    regex = [_span("010101A123N", "finnish_ssn", 7, 18, "regex")]
    merged = hy.merge(model, regex)
    assert len(merged) == 1
    assert merged[0]["type"] == "finnish_ssn"
    assert merged[0]["source"] == "regex"


def test_regex_wins_on_overlapping_ip():
    model = [_span("192.168.1.15", "url", 0, 12, "privacy_filter")]
    regex = [_span("192.168.1.15", "ip", 0, 12, "regex")]
    merged = hy.merge(model, regex)
    assert [m["type"] for m in merged] == ["ip"]


def test_non_overlapping_spans_are_unioned():
    text = "Matti Virtanen 010101A123N"
    model = [_span("Matti Virtanen", "name", 0, 14, "privacy_filter")]
    regex = [_span("010101A123N", "finnish_ssn", 15, 26, "regex")]
    merged = hy.merge(model, regex)
    assert {m["type"] for m in merged} == {"name", "finnish_ssn"}


def test_model_name_kept_when_no_regex_clash():
    # Nimet ovat mallin aluetta; ilman regex-osumaa mallin span sailyy.
    model = [_span("Aino Korhonen", "name", 0, 13, "privacy_filter")]
    regex = []
    merged = hy.merge(model, regex)
    assert len(merged) == 1
    assert merged[0]["type"] == "name"


def test_merged_spans_sorted_by_start():
    model = [_span("Pekka", "name", 20, 25, "privacy_filter")]
    regex = [_span("a@b.fi", "email", 0, 6, "regex")]
    merged = hy.merge(model, regex)
    assert [m["start"] for m in merged] == [0, 20]
