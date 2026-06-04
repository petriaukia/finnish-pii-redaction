"""Liima OpenAI Privacy Filterin kategorioiden ja testisuunnitelman tyyppien valilla.

Privacy Filter palauttaa 8 entity_group-arvoa. Testisuunnitelma (privacy-filter-suomi-
testisuunnitelma.md) kayttaa omia tyyppinimia expected_spans-kentassa. Tama moduuli
maarittelee kaannoksen seka ne tyypit, joita malli EI tunne lainkaan (sotu, IP) ja
jotka odotetaan tulevan vain regex-kerroksesta.
"""

# Mallin entity_group -> testisuunnitelman tyyppi
MODEL_TO_PLAN = {
    "private_person": "name",
    "private_phone": "phone",
    "private_email": "email",
    "private_address": "address",
    "private_date": "date",
    "account_number": "iban",
    "secret": "secret",
    "private_url": "url",
}

# Tyypit joita malli EI tunne kategoriana -> regex on ainoa lahde naille.
REGEX_ONLY_TYPES = {"finnish_ssn", "ip"}

# Kriittisyysoletukset tyypeittain (kaytetaan jos esimerkki ei maaraa kriittisyytta).
DEFAULT_CRITICALITY = {
    "finnish_ssn": "high",
    "ip": "high",
    "iban": "high",
    "email": "medium",
    "phone": "medium",
    "secret": "high",
    "name": "medium",
    "address": "medium",
    "date": "low",
    "url": "low",
}


def map_model_type(entity_group: str) -> str:
    """Kaanna mallin entity_group testisuunnitelman tyypiksi.

    Tuntematon ryhma palautetaan sellaisenaan, jotta uudet kategoriat eivat huku.
    """
    return MODEL_TO_PLAN.get(entity_group, entity_group)
