"""type_mapping: mallin kategoriat <-> testisuunnitelman tyypit."""
import type_mapping as tm


def test_known_model_categories_map_to_plan_types():
    assert tm.map_model_type("private_person") == "name"
    assert tm.map_model_type("private_phone") == "phone"
    assert tm.map_model_type("account_number") == "iban"
    assert tm.map_model_type("private_email") == "email"


def test_unknown_category_passes_through_unchanged():
    # Uudet kategoriat eivat saa hukkua: palautetaan sellaisenaan.
    assert tm.map_model_type("brand_new_category") == "brand_new_category"


def test_ssn_and_ip_are_regex_only():
    # Mallilla ei ole naita kategorioita -> regex on ainoa lahde. Hybridi-teesin ydin.
    assert "finnish_ssn" in tm.REGEX_ONLY_TYPES
    assert "ip" in tm.REGEX_ONLY_TYPES


def test_default_criticality_marks_formal_identifiers_high():
    assert tm.DEFAULT_CRITICALITY["finnish_ssn"] == "high"
    assert tm.DEFAULT_CRITICALITY["ip"] == "high"
    assert tm.DEFAULT_CRITICALITY["iban"] == "high"
