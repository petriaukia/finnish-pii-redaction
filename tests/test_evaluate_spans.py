"""Span-arviointi: typed recall vs redaction recall, vuodot, mislabeled, FP.

Tama on harnessin tarkein logiikka: ilman typed/redaction-erottelua raportti vaittaisi
mallin "osaavan sotun", vaikka se vain maskasi numerot vaaralla tyypilla.
"""
import evaluate_spans as ev


def _expected(text, typ, crit="high"):
    return {"text": text, "type": typ, "criticality": crit}


def _produced(text, typ):
    return {"text": text, "type": typ, "source": "x"}


def test_correct_type_counts_as_typed_and_masked():
    ds = [{"id": "a", "expected_spans": [_expected("010101A123N", "finnish_ssn")]}]
    prod = {"a": [_produced("010101A123N", "finnish_ssn")]}
    r = ev.evaluate_run(ds, prod)
    bt = r["per_type"]["finnish_ssn"]
    assert bt["typed_recall"] == 1.0
    assert bt["redaction_recall"] == 1.0
    assert r["totals"]["n_leaks"] == 0
    assert r["totals"]["n_mislabeled"] == 0


def test_wrong_type_is_masked_but_not_typed():
    # Malli merkitsi sotun ibaniksi: data EI vuoda, mutta taksonomia pielessa.
    ds = [{"id": "a", "expected_spans": [_expected("010101A123N", "finnish_ssn")]}]
    prod = {"a": [_produced("010101A123N", "iban")]}
    r = ev.evaluate_run(ds, prod)
    bt = r["per_type"]["finnish_ssn"]
    assert bt["typed_recall"] == 0.0
    assert bt["redaction_recall"] == 1.0
    assert r["totals"]["n_leaks"] == 0
    assert r["totals"]["n_mislabeled"] == 1
    assert r["mislabeled"][0]["got_type"] == "iban"


def test_unmasked_expected_is_a_leak():
    ds = [{"id": "a", "expected_spans": [_expected("FI21 1234 5600 0007 85", "iban")]}]
    prod = {"a": []}
    r = ev.evaluate_run(ds, prod)
    assert r["totals"]["n_leaks"] == 1
    assert r["false_negatives"][0]["type"] == "iban"
    assert r["per_type"]["iban"]["redaction_recall"] == 0.0


def test_produced_matching_nothing_is_false_positive():
    ds = [{"id": "a", "expected_spans": []}]
    prod = {"a": [_produced("Henkilotunnus", "name")]}
    r = ev.evaluate_run(ds, prod)
    assert r["totals"]["n_false_positives"] == 1
    assert r["false_positives"][0]["produced"] == "Henkilotunnus"


def test_substring_text_match_is_lenient():
    # Odotettu kokonaisuus loytyy vaikka tuotettu span on osajoukko (tai painvastoin).
    ds = [{"id": "a", "expected_spans": [_expected("Matti Virtanen", "name", "medium")]}]
    prod = {"a": [_produced("Matti", "name")]}
    r = ev.evaluate_run(ds, prod)
    assert r["per_type"]["name"]["redaction_recall"] == 1.0


def test_totals_aggregate_across_types():
    ds = [{"id": "a", "expected_spans": [
        _expected("010101A123N", "finnish_ssn"),
        _expected("a@b.fi", "email", "medium"),
    ]}]
    prod = {"a": [_produced("010101A123N", "finnish_ssn"), _produced("a@b.fi", "email")]}
    r = ev.evaluate_run(ds, prod)
    assert r["totals"]["n_expected"] == 2
    assert r["totals"]["typed_found"] == 2
    assert r["totals"]["typed_recall"] == 1.0
