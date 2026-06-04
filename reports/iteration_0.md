# Iteraatio 0 - tulosraportti

## Yhteenveto

- Aineiston koko: 15
- Privacy Filter only: tyypitetty 59 %, maskaus 88 %, vuodot 2, FP 9
- Regex only: tyypitetty 59 %, maskaus 59 %, vuodot 7, FP 0
- Hybrid: tyypitetty 88 %, maskaus 94 %, vuodot 1, FP 9
- Kriittiset vuodot (criticality=high): 2

### Kriittiset vuodot

- Privacy Filter only: iban (id smoke_006, FI21 1234 5600 0007 85)
- Regex only: secret (id smoke_013, sk-test-ABCD1234EFGH5678)

## Ajot per moodi

### Privacy Filter only

- Odotettu: 17  tyypitetty: 10 (59 %)  maskattu: 15 (88 %)
- Vuodot (ei maskattu): 2  vaara tyyppi: 5  false positives: 9

| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |
|---|---:|---:|---:|
| address | 1 | 100 % | 100 % |
| date | 1 | 100 % | 100 % |
| email | 3 | 100 % | 100 % |
| finnish_ssn | 2 | 0 % | 100 % |
| iban | 1 | 0 % | 0 % |
| ip | 2 | 0 % | 100 % |
| name | 4 | 75 % | 75 % |
| phone | 2 | 100 % | 100 % |
| secret | 1 | 0 % | 100 % |

### Regex only

- Odotettu: 17  tyypitetty: 10 (59 %)  maskattu: 10 (59 %)
- Vuodot (ei maskattu): 7  vaara tyyppi: 0  false positives: 0

| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |
|---|---:|---:|---:|
| address | 1 | 0 % | 0 % |
| date | 1 | 0 % | 0 % |
| email | 3 | 100 % | 100 % |
| finnish_ssn | 2 | 100 % | 100 % |
| iban | 1 | 100 % | 100 % |
| ip | 2 | 100 % | 100 % |
| name | 4 | 0 % | 0 % |
| phone | 2 | 100 % | 100 % |
| secret | 1 | 0 % | 0 % |

### Hybrid

- Odotettu: 17  tyypitetty: 15 (88 %)  maskattu: 16 (94 %)
- Vuodot (ei maskattu): 1  vaara tyyppi: 1  false positives: 9

| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |
|---|---:|---:|---:|
| address | 1 | 100 % | 100 % |
| date | 1 | 100 % | 100 % |
| email | 3 | 100 % | 100 % |
| finnish_ssn | 2 | 100 % | 100 % |
| iban | 1 | 100 % | 100 % |
| ip | 2 | 100 % | 100 % |
| name | 4 | 75 % | 75 % |
| phone | 2 | 100 % | 100 % |
| secret | 1 | 0 % | 100 % |

## Vuodot (PII jai kokonaan maskaamatta)

| id | tyyppi | odotettu | kriittisyys | ajo |
|---|---|---|---|---|
| smoke_004 | name | Aino Korhonen | medium | Privacy Filter only |
| smoke_006 | iban | FI21 1234 5600 0007 85 | high | Privacy Filter only |
| smoke_001 | name | Matti Virtanen | medium | Regex only |
| smoke_004 | name | Aino Korhonen | medium | Regex only |
| smoke_009 | date | 4.6.2026 | low | Regex only |
| smoke_010 | address | Mannerheimintie 12 | medium | Regex only |
| smoke_011 | name | Pekka Nieminen | medium | Regex only |
| smoke_013 | secret | sk-test-ABCD1234EFGH5678 | high | Regex only |
| smoke_015 | name | Nguyen Thi Linh | medium | Regex only |
| smoke_004 | name | Aino Korhonen | medium | Hybrid |

## Vaara tyyppi (maskattu, mutta luokiteltu vaarin)

| id | odotettu tyyppi | teksti | mallin tyyppi | ajo |
|---|---|---|---|---|
| smoke_002 | finnish_ssn | 010101A123N | date | Privacy Filter only |
| smoke_003 | ip | 192.168.1.15 | url | Privacy Filter only |
| smoke_007 | ip | 2001:14bb:180:1234::1 | url | Privacy Filter only |
| smoke_008 | finnish_ssn | 131052-308T | date | Privacy Filter only |
| smoke_013 | secret | sk-test-ABCD1234EFGH5678 | iban | Privacy Filter only |
| smoke_013 | secret | sk-test-ABCD1234EFGH5678 | iban | Hybrid |

## False positives (maskattu turhaan)

| id | tyyppi | teksti | ajo |
|---|---|---|---|
| smoke_002 | name | Henkilötunnus | Privacy Filter only |
| smoke_002 | name | . | Privacy Filter only |
| smoke_004 | name | Aino Korhoseen | Privacy Filter only |
| smoke_006 | name | Tilinumero | Privacy Filter only |
| smoke_008 | name | Hakijan henkilötunnus | Privacy Filter only |
| smoke_009 | name | Sopimus allekirjoitettiin | Privacy Filter only |
| smoke_010 | address | oso | Privacy Filter only |
| smoke_010 | address | 00 | Privacy Filter only |
| smoke_012 | iban | 123456789 | Privacy Filter only |
| smoke_002 | name | Henkilötunnus | Hybrid |
| smoke_002 | name | . | Hybrid |
| smoke_004 | name | Aino Korhoseen | Hybrid |
| smoke_006 | name | Tilinumero | Hybrid |
| smoke_008 | name | Hakijan henkilötunnus | Hybrid |
| smoke_009 | name | Sopimus allekirjoitettiin | Hybrid |
| smoke_010 | address | oso | Hybrid |
| smoke_010 | address | 00 | Hybrid |
| smoke_012 | iban | 123456789 | Hybrid |

## Paatos

- [ ] Jatka seuraavaan iteraatioon
- [ ] Korjaa regex
- [ ] Rajaa kayttotapausta
- [ ] Lisaa manuaalinen tarkistus
