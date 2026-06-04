# OpenAI Privacy Filter vs. regex — iteratiivinen testisuunnitelma suomalaiselle henkilödatalle

## 1. Tarkoitus

Tämän testisuunnitelman tarkoitus on arvioida, kuinka hyvin OpenAI Privacy Filter tunnistaa ja maskaa suomalaisessa tekstissä esiintyviä henkilötietoja verrattuna sääntöpohjaiseen regex-kerrokseen.

Tavoite ei ole todistaa, että ratkaisu on “GDPR-yhteensopiva”, vaan selvittää käytännöllisesti:

1. mitä Privacy Filter löytää yksin,
2. mitä regex löytää yksin,
3. mitä jää läpi kummaltakin,
4. millainen kevyt hybridimalli olisi puolustettavissa,
5. missä kohdissa tarvitaan manuaalinen katselmus tai tiukempi prosessi.

Keskeinen periaate: testi tehdään iteratiivisesti. Ensimmäinen kierros saa mennä pieleen. Sen tarkoitus on paljastaa rakenteelliset ongelmat, ei tuottaa lopullista mittaria.

---

## 2. Rajaus

### Mukana testissä

Testataan ainakin seuraavat tietotyypit:

| Tietotyyppi | Privacy Filter -odotus | Regex-odotus | Kommentti |
|---|---:|---:|---|
| Henkilön nimet | korkea mutta epävarma | matala | Malli todennäköisesti parempi kuin regex |
| Puhelinnumerot | keskikorkea | korkea | Suomen numeromuodot kannattaa regexata |
| Sähköpostit | korkea | korkea | Molempien pitäisi löytää |
| Katuosoitteet | keskikorkea | keskitaso | Span accuracy tärkeä |
| Postinumerot ja kaupungit | epävarma | keskitaso | Ei aina yksin henkilötieto |
| Henkilötunnukset | epävarma | erittäin korkea | Ei saa jättää mallin varaan |
| IP-osoitteet | epävarma | erittäin korkea | IPv4 ja IPv6 erikseen |
| IBAN / tilinumerot | keskikorkea | korkea | FI-IBAN regexillä |
| Päivämäärät | korkea | korkea | Kaikki päivämäärät eivät ole henkilötietoja |
| Salaisuudet/API-avaimet | korkea? | keskitaso | Tarvittaessa erillinen secrets-skanneri |
| Epäsuorat tunnisteet | matala | matala | Vaatii manuaalista arviota tai erillistä mallia |

### Ei mukana ensimmäisessä vaiheessa

Ensimmäisessä vaiheessa ei yritetä ratkaista täydellisesti:

- täyttä GDPR-vaatimustenmukaisuutta,
- kaikkia erityisiä henkilötietoryhmiä,
- semanttista anonymisointia,
- organisaatiokohtaista tietosuojapolitiikkaa,
- tuotantokäyttöön hyväksyntää,
- täydellistä benchmarkia.

Nämä voidaan lisätä myöhemmin, jos perusratkaisu näyttää lupaavalta.

---

## 3. Testin pääajatus

Testi ajetaan kolmella tavalla:

1. **Privacy Filter only**
   - Mitataan mallin oma kyky.
   - Ei regex-korjauksia.
   - Tärkeää, jotta malliin ei luoteta väärin.

2. **Regex only**
   - Mitataan suomalaisiin formaatteihin räätälöidyn sääntöpohjaisen tunnistuksen kyky.
   - Hyvä kontrolli formaaleille tunnisteille.

3. **Hybrid**
   - Privacy Filter + regex.
   - Tämä on todennäköisin tuotantokandidaatti.
   - Hyväksyntäarvio tehdään ensisijaisesti hybridille, ei yksittäiselle mallille.

---

## 4. Iteratiivinen etenemismalli

## Iteraatio 0 — ympäristö ja smoke test

### Tavoite

Varmistaa, että testiputki käynnistyy, tulokset tallentuvat ja mallin output saadaan vertailtavaan muotoon.

### Aineisto

10–20 erittäin yksinkertaista synteettistä esimerkkiä.

Esimerkiksi:

```jsonl
{"id":"smoke_001","text":"Matti Virtanen, 040 123 4567, matti.virtanen@example.fi","expected":["Matti Virtanen","040 123 4567","matti.virtanen@example.fi"]}
{"id":"smoke_002","text":"Henkilötunnus on 010101A123N.","expected":["010101A123N"]}
{"id":"smoke_003","text":"Kirjautuminen tuli osoitteesta 192.168.1.15.","expected":["192.168.1.15"]}
```

### Hyväksymiskriteeri

Ei vielä laadullista hyväksyntää.

Riittää, että:

- kaikki kolme ajoa suoritetaan,
- tulokset tallentuvat,
- false negative -lista syntyy,
- tulosformaatti on luettavissa.

### Päätös iteraation jälkeen

Jos putki ei toimi, korjataan vain infra.
Ei vielä viritetä regexejä pitkälle.

---

## Iteraatio 1 — suomalaiset formaalit tunnisteet

### Tavoite

Varmistaa, että sotu, IP, IBAN, sähköposti ja puhelinnumerot saadaan kiinni vähintään regex-kerroksella.

### Aineisto

Noin 50–100 esimerkkiä.

Mukana:

- kelvolliset henkilötunnukset,
- virheelliset henkilötunnuksen kaltaiset merkkijonot,
- IPv4,
- IPv6,
- FI-IBAN,
- sähköpostit,
- suomalaiset puhelinnumeromuodot,
- numeromuotoja, joita ei pidä maskata.

### Testattavat esimerkkityypit

```text
Hakijan henkilötunnus on 131052-308T.
Asiakas ilmoitti numeroksi 040 123 4567.
Puhelin: +358 50 123 4567.
Tilinumero: FI21 1234 5600 0007 85.
Kirjautuminen tuli IP-osoitteesta 2001:14bb:180:1234::1.
Tilausnumero on 123456789, tätä ei välttämättä pidä maskata henkilötietona.
```

### Hyväksymiskriteeri

Hybridin pitäisi löytää:

| Tietotyyppi | Minimitavoite |
|---|---:|
| Henkilötunnus | 100 % |
| Sähköposti | 99–100 % |
| IP-osoite | 99–100 % |
| FI-IBAN | 99–100 % |
| Puhelinnumero | 98–100 % |

Jos sotuja jää läpi, regex-kerros korjataan ennen seuraavaa vaihetta.

### Päätös iteraation jälkeen

- Korjataan vain ilmeiset regex-puutteet.
- Ei vielä optimoida nimiä, osoitteita tai kontekstia.
- Dokumentoidaan Privacy Filterin omat puutteet, mutta ei yritetä pakottaa sitä löytämään formaaleja suomalaisia tunnisteita.

---

## Iteraatio 2 — nimet, osoitteet ja tavallinen suomenkielinen teksti

### Tavoite

Testata mallin hyötyä niissä kohdissa, joissa regex ei ole luonteva ratkaisu.

### Aineisto

Noin 100–200 esimerkkiä.

Mukana:

- suomalaiset nimet,
- vieraskieliset Suomessa tavalliset nimet,
- kaksoisnimet,
- taivutetut nimet,
- osoitteet eri muodoissa,
- asunto-osakkeiden ja kiinteistöjen osoitteet,
- asiakasviestit,
- hallinnolliset tekstit,
- sopimusotteet,
- negatiiviset esimerkit ilman henkilötietoja.

### Esimerkkejä

```text
Ota yhteys Aino-Kaisa Hämäläiseen ennen perjantaita.
Tapasin Nguyen Thi Linhin Teamsissa.
Asiakas asuu osoitteessa Vanha Porvoontie 7 B 12, 04600 Mäntsälä.
Kaupan kohteena on määräala kiinteistöstä, ei koko osoitteessa sijaitseva rakennus.
```

### Arvioitavat asiat

- Löytyykö koko nimi vai vain etunimi/sukunimi?
- Tunnistaako malli taivutetun nimen?
- Tunnistaako malli osoitteen kokonaan?
- Maskataanko liikaa yleisiä sanoja?
- Jääkö osoitteesta osa näkyviin?

### Hyväksymiskriteeri

Tässä ei kannata vaatia täydellisyyttä ensimmäisellä kierroksella.

Käytännöllinen tavoite:

| Tietotyyppi | Tavoite |
|---|---:|
| Selkeät nimet | >95 % |
| Osoitteet | >90–95 % |
| Puhelin/sähköposti/sotu/IP hybridinä | edelleen lähes 100 % |
| False positives | hyväksytään, jos ne eivät riko käyttötapausta |

### Päätös iteraation jälkeen

Jos nimet ja osoitteet toimivat kohtuullisesti, hybridimalli voi olla hyvä “ensimmäinen suojakerros”.

Jos nimet tai osoitteet jäävät usein läpi, käyttötapausta pitää rajata tai lisätä manuaalinen tarkistus.

---

## Iteraatio 3 — epäsuorat tunnisteet ja GDPR-riskitekstit

### Tavoite

Selvittää, missä määrin tekstistä jää tunnistettavia henkilöitä, vaikka klassinen PII poistuu.

Tämä on tärkein GDPR:n kannalta, mutta sitä ei kannata tehdä ensimmäisenä, koska se on tulkinnallista.

### Aineisto

50–100 esimerkkiä korkeamman riskin tekstityypeistä.

Mukana:

- HR-tekstit,
- kunnallishallinnon tekstit,
- terveyteen tai työkykyyn liittyvät kuvaukset,
- lasten ja koulujen kontekstit,
- pienet paikkakunnat,
- harvinaiset roolit,
- yksittäiseen henkilöön viittaavat tapahtumaketjut.

### Esimerkkejä

```text
Kunnan ainoa ruotsinkielinen erityisopettaja jäi sairauslomalle helmikuussa 2025.
Yrityksen CFO, joka aloitti tehtävässä viime viikolla, pyysi käsittelyn rajoittamista.
Pienen kyläkoulun 4. luokan oppilas siirrettiin toiseen ryhmään huoltajan pyynnöstä.
```

### Arviointitapa

Tätä ei arvioida pelkällä span-mittarilla.

Jokaiselle esimerkille merkitään:

| Kenttä | Arvo |
|---|---|
| classical_pii_removed | kyllä / ei |
| still_identifiable | kyllä / ei / ehkä |
| reason | miksi henkilö voisi olla tunnistettavissa |
| recommended_action | hyväksy / maskaa lisää / älä lähetä LLM:lle / manuaalinen tarkistus |

### Hyväksymiskriteeri

Tämän iteraation tarkoitus ei ole saada täydellistä automaatiota.

Hyvä lopputulos on selkeä päätöslogiikka:

- matalan riskin tekstit voidaan ajaa automaattisesti,
- keskitason tekstit vaativat hybridimaskauksen,
- korkean riskin tekstit vaativat manuaalisen tarkistuksen tai eri ympäristön,
- erittäin korkean riskin tekstejä ei lähetetä yleiseen LLM-palveluun.

---

## Iteraatio 4 — regressiotesti ja minimituotantokriteeri

### Tavoite

Kun ensimmäiset virheet on korjattu, lukitaan pieni regressiosetti, joka ajetaan aina muutosten jälkeen.

### Regressiosetin koko

Noin 50–100 esimerkkiä.

Mukana vain edellisissä vaiheissa löydetyt tärkeimmät kompastuskivet.

### Mukaan regressiosettiin

- kaikki sotu-muodot,
- IPv4 ja IPv6,
- FI-IBAN,
- yleisimmät suomalaiset puhelinnumerot,
- 10–20 hankalaa nimeä,
- 10–20 hankalaa osoitetta,
- 5–10 epäsuoraa tunnistettavuutta kuvaavaa tapausta.

### Hyväksymiskriteeri ennen käyttöä

Minimikriteeri hybridille:

| Osa-alue | Ehto |
|---|---|
| Sotu | 0 läpipääsyä regressiosetissä |
| IP | 0 läpipääsyä regressiosetissä, jos mukana riskimallissa |
| Sähköposti | 0 läpipääsyä regressiosetissä |
| Puhelin | 0 kriittistä läpipääsyä regressiosetissä |
| Nimet | tunnetut hankalat nimet eivät saa jäädä järjestelmällisesti läpi |
| Osoitteet | osoitteen olennaiset osat eivät saa jäädä näkyviin |
| Epäsuorat tunnisteet | eivät saa mennä automaattisesti “turvallinen”-luokkaan |

---

## 5. Suositeltu tiedostorakenne

```text
privacy-filter-eval/
  README.md
  test_plan.md

  data/
    iteration_0_smoke.jsonl
    iteration_1_formal_identifiers.jsonl
    iteration_2_names_addresses.jsonl
    iteration_3_contextual_identifiability.jsonl
    regression_set.jsonl

  scripts/
    run_privacy_filter.py
    run_regex_baseline.py
    run_hybrid.py
    evaluate_spans.py
    evaluate_contextual.py

  results/
    iteration_0/
    iteration_1/
    iteration_2/
    iteration_3/
    regression/

  reports/
    false_negatives.md
    false_positives.md
    summary.md
```

---

## 6. Testidatan ehdotettu formaatti

Suositeltu formaatti on JSONL.

### Yksinkertainen span-pohjainen tapaus

```json
{
  "id": "formal_001",
  "text": "Hakijan henkilötunnus on 131052-308T ja puhelin 040 123 4567.",
  "expected_spans": [
    {"text": "131052-308T", "type": "finnish_ssn", "criticality": "high"},
    {"text": "040 123 4567", "type": "phone", "criticality": "medium"}
  ],
  "risk_level": "medium",
  "notes": "sotu + suomalainen puhelinnumero"
}
```

### Kontekstuaalinen tapaus

```json
{
  "id": "context_001",
  "text": "Kunnan ainoa ruotsinkielinen erityisopettaja jäi sairauslomalle helmikuussa 2025.",
  "expected_spans": [],
  "contextual_risk": {
    "still_identifiable": "maybe",
    "reason": "Harvinainen rooli, pieni organisaatio ja tarkka ajankohta voivat tunnistaa henkilön.",
    "recommended_action": "manual_review"
  },
  "risk_level": "high"
}
```

---

## 7. Regex-kerroksen ensimmäinen sisältö

Ensimmäisessä versiossa regexejä ei pidä yrittää tehdä täydellisiksi.

Mukana kuitenkin vähintään:

1. suomalainen henkilötunnus,
2. sähköposti,
3. suomalaiset puhelinnumerot,
4. IPv4,
5. IPv6,
6. FI-IBAN,
7. mahdolliset API-avaimen kaltaiset salaisuudet, jos relevanttia.

### Huomio henkilötunnuksesta

Henkilötunnuksen regexissä kannattaa huomioida:

- vanhat välimerkit: `+`, `-`, `A`,
- mahdolliset uudet välimerkit: `B`, `C`, `D`, `E`, `F`, `Y`, `X`, `W`, `V`, `U`,
- tarkistusmerkin merkkijoukko.

Ensimmäinen regex voi olla ylikattava. Parempi false positive kuin sotu läpi.

---

## 8. Raportointi

Jokaisesta iteraatiosta tuotetaan lyhyt raportti.

### Raportin rakenne

```markdown
# Iteraatio N — tulosraportti

## Yhteenveto

- Aineiston koko:
- Privacy Filter only:
- Regex only:
- Hybrid:
- Kriittiset false negativet:
- Suositeltu seuraava toimenpide:

## Tärkeimmät löydökset

## False negatives

| id | tyyppi | odotettu | mikä jäi läpi | ajo |
|---|---|---|---|---|

## False positives

| id | tyyppi | mitä maskattiin turhaan | vaikutus |
|---|---|---|---|

## Päätös

- Jatka seuraavaan iteraatioon
- Korjaa regex
- Rajaa käyttötapausta
- Lisää manuaalinen tarkistus
- Lopeta testaus, jos ratkaisu ei näytä lupaavalta
```

---

## 9. Päätöslogiikka

Testin jälkeen ratkaisua ei pidä hyväksyä yhdellä yleisellä arvosanalla.

Käytä sen sijaan tätä päätöslogiikkaa:

| Löydös | Päätös |
|---|---|
| Sotuja jää läpi hybridissä | Ei käyttöön ennen regex-korjausta |
| IP:t jäävät läpi ja IP:t ovat käyttötapauksessa henkilötietoja | Ei käyttöön ennen regex-korjausta |
| Nimiä jää satunnaisesti läpi | Käyttö vain matalan/keskitason riskissä tai manuaalisella tarkistuksella |
| Osoitteet jäävät osittain näkyviin | Lisää regex/post-processing tai rajaa käyttöä |
| Epäsuorat tunnisteet jäävät usein näkyviin | Ei saa väittää anonymisoinniksi |
| False positiveja paljon | Arvioi haitta käyttötarkoitukselle, mutta tietosuojan kannalta usein hyväksyttävää |
| Malli toimii vain helpoissa tapauksissa | Käytä vain apukerroksena, ei kontrollina |

---

## 10. Mitä ei pidä tehdä liian aikaisin

Vältä alussa:

- täydellisen testikehikon rakentamista,
- liian suurta synteettistä aineistoa,
- monimutkaista annotointityökalua,
- liian tarkkaa F1-optimointia,
- mallin fine-tunetusta,
- regexien loputonta hiontaa,
- epäsuoran tunnistettavuuden automaattista ratkaisemista.

Ensimmäinen tavoite on löytää suuret riskit nopeasti.

---

## 11. Minimitulos, joka olisi käytännössä hyödyllinen

Testin jälkeen pitäisi pystyä sanomaan esimerkiksi:

```text
Privacy Filter toimii hyödyllisenä ensimmäisenä kerroksena nimille, osoitteille, sähköposteille ja puhelinnumeroille, mutta se ei yksin riitä suomalaiseen henkilödatan poistoon. Henkilötunnukset, IP-osoitteet, FI-IBANit ja suomalaiset puhelinnumeromuodot tulee käsitellä erillisellä regex-kerroksella. Ratkaisua ei tule kutsua anonymisoinniksi ilman erillistä kontekstuaalisen tunnistettavuuden arviointia.
```

Tai vaihtoehtoisesti:

```text
Privacy Filter ei toiminut riittävän luotettavasti suomenkielisissä nimi- ja osoitetapauksissa. Sitä voidaan käyttää vain apuna, ei varsinaisena tietosuojakontrollina.
```

Molemmat ovat hyviä lopputuloksia, jos ne perustuvat havaintoihin.

---

## 12. Käytännön seuraava askel

Aloita iteraatiolla 0 ja 1.

Älä rakenna vielä täydellistä GDPR-arviointia.

Ensimmäinen tavoite:

1. saada ajoputki toimimaan,
2. nähdä mallin raakasuorituskyky,
3. varmistaa, että regex löytää sotu- ja IP-tapaukset,
4. kerätä ensimmäiset false negative -esimerkit.

Kun nämä ovat kunnossa, päätetään vasta seuraavan kierroksen tarkkuudesta.
