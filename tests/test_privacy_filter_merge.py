"""Privacy Filter -runnerin span-yhdistys ja detect() ilman mallin latausta.

_merge_adjacent on puhdas funktio joka ottaa pipeline-tyyliset dictit -> ei tarvitse
torchia/mallia. detect() testataan monkeypatchaamalla get_pipeline.
"""
import run_privacy_filter as pf


def _ent(group, start, end, score=0.99, word=""):
    return {"entity_group": group, "start": start, "end": end, "score": score, "word": word}


def test_merge_joins_name_split_by_space():
    # Regressio: BIOES-tagit eivat yhdisty transformersin "simple"-aggregaatiossa.
    text = "Harry Potter soitti."
    raw = [_ent("private_person", 0, 5), _ent("private_person", 6, 12)]
    merged = pf._merge_adjacent(raw, text)
    assert len(merged) == 1
    assert text[merged[0]["start"]:merged[0]["end"]] == "Harry Potter"


def test_merge_joins_email_split_contiguous():
    text = "x harry.potter@hogwarts.edu y"
    # email pilkkoutui kahteen perakkaiseen palaan ilman valia
    raw = [_ent("private_email", 2, 23), _ent("private_email", 23, 27)]
    merged = pf._merge_adjacent(raw, text)
    assert len(merged) == 1
    assert text[merged[0]["start"]:merged[0]["end"]] == "harry.potter@hogwarts.edu"


def test_merge_does_not_join_different_types():
    text = "Matti 040 1234"
    raw = [_ent("private_person", 0, 5), _ent("private_phone", 6, 14)]
    merged = pf._merge_adjacent(raw, text)
    assert len(merged) == 2


def test_merge_does_not_join_across_nonspace_gap():
    # Vali sisaltaa sanan "ja" -> ei saa yhdistaa kahta eri henkiloa.
    text = "Matti ja Pekka"
    raw = [_ent("private_person", 0, 5), _ent("private_person", 9, 14)]
    merged = pf._merge_adjacent(raw, text)
    assert len(merged) == 2


def test_merge_takes_minimum_score():
    text = "Harry Potter"
    raw = [_ent("private_person", 0, 5, score=0.9), _ent("private_person", 6, 12, score=0.5)]
    merged = pf._merge_adjacent(raw, text)
    assert merged[0]["score"] == 0.5


def test_detect_maps_types_and_strips_whitespace(monkeypatch):
    text = "Harry Potter, harry@x.edu"

    def fake_pipeline(t):
        return [
            {"entity_group": "private_person", "start": 0, "end": 5, "score": 1.0, "word": "Harry"},
            {"entity_group": "private_person", "start": 6, "end": 12, "score": 1.0, "word": "Potter"},
            {"entity_group": "private_email", "start": 14, "end": 25, "score": 1.0, "word": "harry@x.edu"},
        ]

    monkeypatch.setattr(pf, "get_pipeline", lambda device=None: fake_pipeline)
    spans = pf.detect(text)
    by_type = {s["type"]: s for s in spans}
    assert by_type["name"]["text"] == "Harry Potter"      # yhdistetty + ei etuvalia
    assert by_type["email"]["text"] == "harry@x.edu"
    assert all(s["source"] == "privacy_filter" for s in spans)
