# Iteraatio 1 - tulosraportti

## Yhteenveto

- Aineiston koko: 51
- Privacy Filter only: tyypitetty 51 %, maskaus 78 %, vuodot 11, FP 25
- Regex only: tyypitetty 86 %, maskaus 86 %, vuodot 7, FP 0
- Hybrid: tyypitetty 98 %, maskaus 98 %, vuodot 1, FP 25
- Kriittiset vuodot (criticality=high): 10

### Kriittiset vuodot

- Privacy Filter only: finnish_ssn (id ssn_006, 070770Y456H)
- Privacy Filter only: ip (id ip_006, ::1)
- Privacy Filter only: ip (id ip_007, 1.2.3.4)
- Privacy Filter only: ip (id ip_008, 10.0.0.1)
- Privacy Filter only: ip (id ip_008, 10.0.0.2)
- Privacy Filter only: ip (id ip_008, 10.0.0.3)
- Privacy Filter only: iban (id iban_001, FI21 1234 5600 0007 85)
- Privacy Filter only: ip (id mix_003, 192.168.1.15)
- Privacy Filter only: finnish_ssn (id mix_003, 010101A123N)
- Privacy Filter only: secret (id mix_005, ghp-abcdef1234567890abcd)

## Ajot per moodi

### Privacy Filter only

- Odotettu: 51  tyypitetty: 26 (51 %)  maskattu: 40 (78 %)
- Vuodot (ei maskattu): 11  vaara tyyppi: 14  false positives: 25

| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |
|---|---:|---:|---:|
| address | 2 | 100 % | 100 % |
| date | 2 | 100 % | 100 % |
| email | 8 | 100 % | 100 % |
| finnish_ssn | 10 | 0 % | 80 % |
| iban | 4 | 75 % | 75 % |
| ip | 12 | 0 % | 50 % |
| name | 2 | 100 % | 100 % |
| phone | 9 | 100 % | 100 % |
| secret | 1 | 0 % | 0 % |
| url | 1 | 0 % | 0 % |

### Regex only

- Odotettu: 51  tyypitetty: 44 (86 %)  maskattu: 44 (86 %)
- Vuodot (ei maskattu): 7  vaara tyyppi: 0  false positives: 0

| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |
|---|---:|---:|---:|
| address | 2 | 0 % | 0 % |
| date | 2 | 0 % | 0 % |
| email | 8 | 100 % | 100 % |
| finnish_ssn | 10 | 100 % | 100 % |
| iban | 4 | 100 % | 100 % |
| ip | 12 | 100 % | 100 % |
| name | 2 | 0 % | 0 % |
| phone | 9 | 100 % | 100 % |
| secret | 1 | 100 % | 100 % |
| url | 1 | 0 % | 0 % |

### Hybrid

- Odotettu: 51  tyypitetty: 50 (98 %)  maskattu: 50 (98 %)
- Vuodot (ei maskattu): 1  vaara tyyppi: 0  false positives: 25

| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |
|---|---:|---:|---:|
| address | 2 | 100 % | 100 % |
| date | 2 | 100 % | 100 % |
| email | 8 | 100 % | 100 % |
| finnish_ssn | 10 | 100 % | 100 % |
| iban | 4 | 100 % | 100 % |
| ip | 12 | 100 % | 100 % |
| name | 2 | 100 % | 100 % |
| phone | 9 | 100 % | 100 % |
| secret | 1 | 100 % | 100 % |
| url | 1 | 0 % | 0 % |

## Vuodot (PII jai kokonaan maskaamatta)

| id | tyyppi | odotettu | kriittisyys | ajo |
|---|---|---|---|---|
| ssn_006 | finnish_ssn | 070770Y456H | high | Privacy Filter only |
| ip_006 | ip | ::1 | high | Privacy Filter only |
| ip_007 | ip | 1.2.3.4 | high | Privacy Filter only |
| ip_008 | ip | 10.0.0.1 | high | Privacy Filter only |
| ip_008 | ip | 10.0.0.2 | high | Privacy Filter only |
| ip_008 | ip | 10.0.0.3 | high | Privacy Filter only |
| iban_001 | iban | FI21 1234 5600 0007 85 | high | Privacy Filter only |
| mix_003 | ip | 192.168.1.15 | high | Privacy Filter only |
| mix_003 | finnish_ssn | 010101A123N | high | Privacy Filter only |
| mix_005 | secret | ghp-abcdef1234567890abcd | high | Privacy Filter only |
| url_001 | url | https://example.fi/kayttaja/matti | low | Privacy Filter only |
| mix_001 | name | Matti Virtanen | medium | Regex only |
| mix_004 | name | Pekka Nieminen | medium | Regex only |
| date_001 | date | 1.1.2025 | low | Regex only |
| date_002 | date | 13.10.1952 | medium | Regex only |
| url_001 | url | https://example.fi/kayttaja/matti | low | Regex only |
| addr_001 | address | Mannerheimintie 12 | medium | Regex only |
| addr_002 | address | Vanha Porvoontie 7 B 12 | medium | Regex only |
| url_001 | url | https://example.fi/kayttaja/matti | low | Hybrid |

## Vaara tyyppi (maskattu, mutta luokiteltu vaarin)

| id | odotettu tyyppi | teksti | mallin tyyppi | ajo |
|---|---|---|---|---|
| ssn_001 | finnish_ssn | 131052-308T | phone | Privacy Filter only |
| ssn_002 | finnish_ssn | 010101A123N | iban | Privacy Filter only |
| ssn_003 | finnish_ssn | 290236+1230 | address | Privacy Filter only |
| ssn_005 | finnish_ssn | 311299B999X | address | Privacy Filter only |
| ssn_008 | finnish_ssn | 010180-123A | address | Privacy Filter only |
| ssn_008 | finnish_ssn | 020290-456B | iban | Privacy Filter only |
| ssn_009 | finnish_ssn | 151199C234K | iban | Privacy Filter only |
| ip_001 | ip | 192.168.1.15 | url | Privacy Filter only |
| ip_002 | ip | 8.8.8.8 | url | Privacy Filter only |
| ip_003 | ip | 255.255.255.0 | phone | Privacy Filter only |
| ip_004 | ip | 2001:14bb:180:1234::1 | url | Privacy Filter only |
| ip_005 | ip | fe80:0000:0000:0000:0202:b3ff:fe1e:8329 | url | Privacy Filter only |
| mix_001 | finnish_ssn | 131052-308T | phone | Privacy Filter only |
| mix_005 | ip | 10.1.2.3 | url | Privacy Filter only |

## False positives (maskattu turhaan)

| id | tyyppi | teksti | ajo |
|---|---|---|---|
| ssn_001 | name | Hakijan henkilotunnus | Privacy Filter only |
| ssn_002 | name | Henkilotunnus | Privacy Filter only |
| ssn_006 | name | Tunnus | Privacy Filter only |
| ssn_006 | name | jarjestelmassa | Privacy Filter only |
| ssn_007 | phone | 45 | Privacy Filter only |
| ssn_009 | name | Tunnus | Privacy Filter only |
| ssn_009 | name | paivitettiin | Privacy Filter only |
| ip_003 | name | Raja-arvo | Privacy Filter only |
| ip_003 | name | aliverkkomaski | Privacy Filter only |
| ip_005 | name | reitittimelta | Privacy Filter only |
| iban_001 | name | Tilinumero | Privacy Filter only |
| email_004 | name | Tavutus rivin lopussa | Privacy Filter only |
| phone_002 | name | Puhelin | Privacy Filter only |
| phone_003 | name | Soita | Privacy Filter only |
| phone_003 | date | heti | Privacy Filter only |
| neg_001 | iban | 123456789 | Privacy Filter only |
| neg_002 | iban | ABC-12345 | Privacy Filter only |
| neg_005 | date | 12.04.2 | Privacy Filter only |
| mix_001 | name | sotu | Privacy Filter only |
| mix_001 | name | soitti numerosta | Privacy Filter only |
| date_001 | name | Sopimus voimassa | Privacy Filter only |
| date_001 | name | alkaen | Privacy Filter only |
| addr_001 | address | oso | Privacy Filter only |
| addr_001 | address | 00 | Privacy Filter only |
| addr_002 | address | 04600 Mantsala | Privacy Filter only |
| ssn_001 | name | Hakijan henkilotunnus | Hybrid |
| ssn_002 | name | Henkilotunnus | Hybrid |
| ssn_006 | name | Tunnus | Hybrid |
| ssn_006 | name | jarjestelmassa | Hybrid |
| ssn_007 | phone | 45 | Hybrid |
| ssn_009 | name | Tunnus | Hybrid |
| ssn_009 | name | paivitettiin | Hybrid |
| ip_003 | name | Raja-arvo | Hybrid |
| ip_003 | name | aliverkkomaski | Hybrid |
| ip_005 | name | reitittimelta | Hybrid |
| iban_001 | name | Tilinumero | Hybrid |
| email_004 | name | Tavutus rivin lopussa | Hybrid |
| phone_002 | name | Puhelin | Hybrid |
| phone_003 | name | Soita | Hybrid |
| phone_003 | date | heti | Hybrid |
| neg_001 | iban | 123456789 | Hybrid |
| neg_002 | iban | ABC-12345 | Hybrid |
| neg_005 | date | 12.04.2 | Hybrid |
| mix_001 | name | sotu | Hybrid |
| mix_001 | name | soitti numerosta | Hybrid |
| date_001 | name | Sopimus voimassa | Hybrid |
| date_001 | name | alkaen | Hybrid |
| addr_001 | address | oso | Hybrid |
| addr_001 | address | 00 | Hybrid |
| addr_002 | address | 04600 Mantsala | Hybrid |

## Paatos

- [ ] Jatka seuraavaan iteraatioon
- [ ] Korjaa regex
- [ ] Rajaa kayttotapausta
- [ ] Lisaa manuaalinen tarkistus
