# Iteraatio 2 - tulosraportti

## Yhteenveto

- Aineiston koko: 45
- Privacy Filter only: tyypitetty 56 %, maskaus 67 %, vuodot 16, FP 16
- Regex only: tyypitetty 0 %, maskaus 0 %, vuodot 48, FP 0
- Hybrid: tyypitetty 56 %, maskaus 67 %, vuodot 16, FP 16
- Kriittiset vuodot (criticality=high): 0

## Ajot per moodi

### Privacy Filter only

- Odotettu: 48  tyypitetty: 27 (56 %)  maskattu: 32 (67 %)
- Vuodot (ei maskattu): 16  vaara tyyppi: 5  false positives: 16

| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |
|---|---:|---:|---:|
| address | 15 | 40 % | 60 % |
| name | 33 | 64 % | 70 % |

### Regex only

- Odotettu: 48  tyypitetty: 0 (0 %)  maskattu: 0 (0 %)
- Vuodot (ei maskattu): 48  vaara tyyppi: 0  false positives: 0

| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |
|---|---:|---:|---:|
| address | 15 | 0 % | 0 % |
| name | 33 | 0 % | 0 % |

### Hybrid

- Odotettu: 48  tyypitetty: 27 (56 %)  maskattu: 32 (67 %)
- Vuodot (ei maskattu): 16  vaara tyyppi: 5  false positives: 16

| Tyyppi | Odotettu | Tyypitetty recall | Maskaus recall |
|---|---:|---:|---:|
| address | 15 | 40 % | 60 % |
| name | 33 | 64 % | 70 % |

## Vuodot (PII jai kokonaan maskaamatta)

| id | tyyppi | odotettu | kriittisyys | ajo |
|---|---|---|---|---|
| name_001 | name | Aino-Kaisa Hämäläiseen | medium | Privacy Filter only |
| name_004 | name | Liisalle | medium | Privacy Filter only |
| name_008 | name | Jukka Mäkelä | medium | Privacy Filter only |
| name_012 | name | Sannalta | medium | Privacy Filter only |
| name_012 | name | Eemeliltä | medium | Privacy Filter only |
| name_014 | name | Olli | medium | Privacy Filter only |
| name_019 | name | Leenalta | medium | Privacy Filter only |
| name_020 | name | Satu Mäkinen | medium | Privacy Filter only |
| name_020 | name | Timo Laine | medium | Privacy Filter only |
| addr_004 | address | Kauppakatu 3 | medium | Privacy Filter only |
| addr_007 | address | Pitkäniementie 220 | medium | Privacy Filter only |
| addr_008 | address | Esplanadi 2 B 7 | medium | Privacy Filter only |
| addr_010 | address | Koivutie 5 | medium | Privacy Filter only |
| mix_002 | address | Kauppakatu 3 | medium | Privacy Filter only |
| name_023 | name | Kimmo | medium | Privacy Filter only |
| addr_012 | address | Järvitie 14 | medium | Privacy Filter only |
| name_001 | name | Aino-Kaisa Hämäläiseen | medium | Regex only |
| name_002 | name | Nguyen Thi Linhin | medium | Regex only |
| name_003 | name | Pekka Nieminen | medium | Regex only |
| name_004 | name | Liisalle | medium | Regex only |
| name_005 | name | Matti Virtanen | medium | Regex only |
| name_005 | name | Anna Korhonen | medium | Regex only |
| name_006 | name | Heikki Saarisen | medium | Regex only |
| name_007 | name | Maria García-López | medium | Regex only |
| name_008 | name | Jukka Mäkelä | medium | Regex only |
| name_009 | name | Karin | medium | Regex only |
| name_009 | name | Tuomaksen | medium | Regex only |
| name_010 | name | Veli-Matti Korhonen | medium | Regex only |
| name_011 | name | Mohammed Al-Rashid | medium | Regex only |
| name_012 | name | Sannalta | medium | Regex only |
| name_012 | name | Eemeliltä | medium | Regex only |
| name_013 | name | Riitta Raesmaa-Aukia | medium | Regex only |
| name_014 | name | Olli | medium | Regex only |
| name_015 | name | Wang Weille | medium | Regex only |
| name_016 | name | Anneli Tuominen-Virtanen | medium | Regex only |
| name_017 | name | Petelle | medium | Regex only |
| name_017 | name | Maijalle | medium | Regex only |
| name_018 | name | Jaakko Hintikka | medium | Regex only |
| name_019 | name | Leenalta | medium | Regex only |
| name_020 | name | Satu Mäkinen | medium | Regex only |
| name_020 | name | Timo Laine | medium | Regex only |
| addr_001 | address | Mannerheimintie 12 | medium | Regex only |
| addr_002 | address | Vanha Porvoontie 7 B 12 | medium | Regex only |
| addr_003 | address | Aleksanterinkatu 15 A | medium | Regex only |
| addr_004 | address | Kauppakatu 3 | medium | Regex only |
| addr_005 | address | Rauhankatu 8 as 4 | medium | Regex only |
| addr_006 | address | PL 105 | medium | Regex only |
| addr_007 | address | Pitkäniementie 220 | medium | Regex only |
| addr_008 | address | Esplanadi 2 B 7 | medium | Regex only |
| addr_009 | address | Yliopistonkatu 4 | low | Regex only |
| addr_010 | address | Koivutie 5 | medium | Regex only |
| mix_001 | name | Matti Virtanen | medium | Regex only |
| mix_001 | address | Mannerheimintie 12 | medium | Regex only |
| mix_002 | name | Anna Korhoselle | medium | Regex only |
| mix_002 | address | Kauppakatu 3 | medium | Regex only |
| mix_003 | name | Pekka Laine | medium | Regex only |
| mix_003 | address | Rauhankatu 8 as 4 | medium | Regex only |
| name_021 | name | Sofia Andersson | medium | Regex only |
| name_022 | name | Jari-Pekalle | medium | Regex only |
| name_023 | name | Kimmo | medium | Regex only |
| addr_011 | address | Teollisuuskatu 21 | low | Regex only |
| addr_012 | address | Järvitie 14 | medium | Regex only |
| name_024 | name | Eeva Aalto | medium | Regex only |
| name_024 | name | Lauri Salo | medium | Regex only |
| name_001 | name | Aino-Kaisa Hämäläiseen | medium | Hybrid |
| name_004 | name | Liisalle | medium | Hybrid |
| name_008 | name | Jukka Mäkelä | medium | Hybrid |
| name_012 | name | Sannalta | medium | Hybrid |
| name_012 | name | Eemeliltä | medium | Hybrid |
| name_014 | name | Olli | medium | Hybrid |
| name_019 | name | Leenalta | medium | Hybrid |
| name_020 | name | Satu Mäkinen | medium | Hybrid |
| name_020 | name | Timo Laine | medium | Hybrid |
| addr_004 | address | Kauppakatu 3 | medium | Hybrid |
| addr_007 | address | Pitkäniementie 220 | medium | Hybrid |
| addr_008 | address | Esplanadi 2 B 7 | medium | Hybrid |
| addr_010 | address | Koivutie 5 | medium | Hybrid |
| mix_002 | address | Kauppakatu 3 | medium | Hybrid |
| name_023 | name | Kimmo | medium | Hybrid |
| addr_012 | address | Järvitie 14 | medium | Hybrid |

## Vaara tyyppi (maskattu, mutta luokiteltu vaarin)

| id | odotettu tyyppi | teksti | mallin tyyppi | ajo |
|---|---|---|---|---|
| name_013 | name | Riitta Raesmaa-Aukia | address | Privacy Filter only |
| addr_002 | address | Vanha Porvoontie 7 B 12 | name | Privacy Filter only |
| addr_009 | address | Yliopistonkatu 4 | name | Privacy Filter only |
| name_022 | name | Jari-Pekalle | address | Privacy Filter only |
| addr_011 | address | Teollisuuskatu 21 | name | Privacy Filter only |
| name_013 | name | Riitta Raesmaa-Aukia | address | Hybrid |
| addr_002 | address | Vanha Porvoontie 7 B 12 | name | Hybrid |
| addr_009 | address | Yliopistonkatu 4 | name | Hybrid |
| name_022 | name | Jari-Pekalle | address | Hybrid |
| addr_011 | address | Teollisuuskatu 21 | name | Hybrid |

## False positives (maskattu turhaan)

| id | tyyppi | teksti | ajo |
|---|---|---|---|
| name_009 | name | Hanke | Privacy Filter only |
| name_011 | name | ana oli | Privacy Filter only |
| name_016 | name | Laskun | Privacy Filter only |
| addr_001 | address | oso | Privacy Filter only |
| addr_001 | address | 00 | Privacy Filter only |
| addr_002 | name | 04600 Mäntsälä | Privacy Filter only |
| addr_006 | address | Lasku | Privacy Filter only |
| addr_007 | address | 362 | Privacy Filter only |
| addr_009 | name | 001 | Privacy Filter only |
| addr_009 | phone | 00 | Privacy Filter only |
| addr_009 | name | Helsinki | Privacy Filter only |
| addr_011 | name | Varasto | Privacy Filter only |
| addr_011 | name | 005 | Privacy Filter only |
| addr_011 | address | 10 | Privacy Filter only |
| addr_011 | name | Helsinki | Privacy Filter only |
| name_024 | name | Allekirjoittajat | Privacy Filter only |
| name_009 | name | Hanke | Hybrid |
| name_011 | name | ana oli | Hybrid |
| name_016 | name | Laskun | Hybrid |
| addr_001 | address | oso | Hybrid |
| addr_001 | address | 00 | Hybrid |
| addr_002 | name | 04600 Mäntsälä | Hybrid |
| addr_006 | address | Lasku | Hybrid |
| addr_007 | address | 362 | Hybrid |
| addr_009 | name | 001 | Hybrid |
| addr_009 | phone | 00 | Hybrid |
| addr_009 | name | Helsinki | Hybrid |
| addr_011 | name | Varasto | Hybrid |
| addr_011 | name | 005 | Hybrid |
| addr_011 | address | 10 | Hybrid |
| addr_011 | name | Helsinki | Hybrid |
| name_024 | name | Allekirjoittajat | Hybrid |

## Paatos

- [ ] Jatka seuraavaan iteraatioon
- [ ] Korjaa regex
- [ ] Rajaa kayttotapausta
- [ ] Lisaa manuaalinen tarkistus
