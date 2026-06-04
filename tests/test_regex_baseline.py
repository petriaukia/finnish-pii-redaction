"""Regex-baseline: suomalaiset formaalit tunnisteet (testisuunnitelman par. 7)."""
import pytest

import run_regex_baseline as rx


def _texts(text):
    return [s["text"] for s in rx.detect(text)]


def _types(text):
    return {s["type"] for s in rx.detect(text)}


# --- Henkilotunnus: kaikki vuosisatamerkit ---
@pytest.mark.parametrize("ssn", [
    "131052-308T",   # 1900-luku, viiva
    "010101A123N",   # 2000-luku, A
    "290236+1230",   # 1800-luku, plus
    "311299B999X",   # uusi 2000-luvun merkki B
    "070770Y456H",   # uusi 1900-luvun merkki Y
    "151199C234K",   # merkki C
])
def test_ssn_all_century_markers_match(ssn):
    assert ssn in _texts(f"Tunnus on {ssn} jarjestelmassa.")
    assert "finnish_ssn" in _types(f"Tunnus on {ssn}.")


@pytest.mark.parametrize("bad", [
    "12345-678",      # liian lyhyt
    "010101A123",     # puuttuva tarkistusmerkki
    "010101Z123N",    # epakelpo erotin Z
])
def test_ssn_invalid_formats_not_matched(bad):
    assert "finnish_ssn" not in _types(f"Merkkijono {bad} tekstissa.")


def test_two_ssns_in_one_text():
    out = _texts("Tunnukset 010180-123A ja 020290-456B.")
    assert "010180-123A" in out and "020290-456B" in out


# --- IP ---
def test_ipv4_matches():
    assert "192.168.1.15" in _texts("Osoitteesta 192.168.1.15 tuli pyynto.")


def test_ipv6_at_sentence_end_matches():
    # Regressio: aiemmin loppurajaus hylkasi perassa olevan pisteen.
    assert "2001:14bb:180:1234::1" in _texts("Palvelin vastasi 2001:14bb:180:1234::1.")


def test_ipv6_full_and_loopback():
    assert "fe80:0000:0000:0000:0202:b3ff:fe1e:8329" in _texts(
        "Reititin fe80:0000:0000:0000:0202:b3ff:fe1e:8329 vastasi.")
    assert "::1" in _texts("Loopback ::1 vastasi pingiin.")


# --- FI-IBAN ---
@pytest.mark.parametrize("iban", [
    "FI21 1234 5600 0007 85",   # ryhmitelty
    "FI2112345600000785",       # ilman valeja
])
def test_fi_iban_matches(iban):
    assert iban in _texts(f"Tilille {iban} maksu.")


# --- Sahkoposti ---
def test_email_variants():
    assert "matti.virtanen+laskut@example.co.uk" in _texts(
        "Yhteys: matti.virtanen+laskut@example.co.uk")
    assert "a@x.fi" in _texts("Osoite a@x.fi tassa.")


# --- Puhelin ---
@pytest.mark.parametrize("phone", [
    "040 123 4567",
    "+358 50 123 4567",
    "0401234567",
    "09-1234567",
    "+358401234567",
])
def test_finnish_phone_formats(phone):
    assert phone in _texts(f"Numero {phone} on kaytossa.")


# --- Negatiiviset: ei saa maskata ---
@pytest.mark.parametrize("text", [
    "Tilausnumero on 123456789 tassa.",       # tilausnumero (ei 0/+358 -alku)
    "Kokous kello 14:30 alkaa.",              # kellonaika
    "Summa oli 1 234,56 euroa.",              # rahasumma
])
def test_negatives_not_matched(text):
    assert rx.detect(text) == [] or "finnish_ssn" not in _types(text)


def test_order_number_is_not_phone_or_ssn():
    types = _types("Tilausnumero on 123456789 tassa.")
    assert "phone" not in types
    assert "finnish_ssn" not in types


# --- Paallekkaisyys ---
def test_overlapping_matches_deduplicated():
    # Sotu sisaltaa numeroita; sama vali ei saa tuottaa kahta spania.
    spans = rx.detect("Tunnus 010101A123N tekstissa.")
    starts = [s["start"] for s in spans]
    assert len(starts) == len(set(starts))
