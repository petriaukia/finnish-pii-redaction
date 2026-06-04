# Suorituskyky: OpenAI Privacy Filter tällä koneella (Apple Silicon, 16 GB)

Mittauksen kysymys: onko malli palveluun riittävän nopea ja kevyt? Tämä ratkaisee
arvon riippumatta tarkkuudesta.

## Tulokset

Korpus: edustavaa suomenkielistä testidataa toistettuna. CPU = kaikki ytimet.
Aika/MB on ekstrapoloitu mitatusta otoksesta (0,03–0,12 MB), batch-luvut mitattu 0,12 MB:llä.

| Ajotapa | per pala (2 kB) | läpäisy | aika / 1 MB | huippu-RSS |
|---|---:|---:|---:|---:|
| transformers fp32, **MPS** (oletus) | ~6,5 s | 0,3 kB/s | **~54 min** | — |
| transformers fp32, **CPU** | ~1,86 s | 1,1 kB/s | ~15,5 min | 3,4 GB |
| **ONNX int8, CPU** (yksi) | ~0,43 s | 4,7 kB/s | ~3,5 min | 3,9 GB |
| ONNX q4, CPU (yksi) | ~0,43 s | 4,7 kB/s | ~3,6 min | 3,9 GB |
| **ONNX int8, CPU, batch=32** | — | 8,5 kB/s | **~2,0 min** | 3,9 GB |

**Per-viesti-latenssi** (tyypillinen chat-viesti, 1,44 kB, useita PII-kohteita, int8): **315 ms.**

Mallin lataus: ~7 s (eager), ONNX-painon lataus HF:stä ensimmäisellä kerralla 18–40 s.

## Kolme johtopäätöstä

1. **Naiivi polku on ansa.** Mallikortin ilmeinen esimerkki (`transformers`-pipeline) ja
   `device="mps"` antavat ~54 min/MB — ja MPS on **hitaampi kuin CPU** tällä mallilla, koska
   MoE-operaatiot putoavat takaisin CPU:lle. Kehittäjä joka kopioi esimerkin päättelisi
   virheellisesti "liian hidas". Lisäksi 16 GB:n koneella muistipaine + swap moninkertaistaa
   hitauden (malli vie ~3,4–3,9 GB; sulje muut softat).

2. **Optimoitu polku on ~8x nopeampi.** Kvantisoitu ONNX (int8/q4) + batchaus: ~2 min/MB,
   ~3,9 GB muistia, ei GPU:ta. Tämä on se polku jota selaimet (transformers.js) käyttävät.
   Mutta sitä ei saa ilmaiseksi — pitää tietää hakea `onnx/model_quantized.onnx` ja ajaa
   onnxruntimella, ei oletus-pipelinellä.

3. **"Halpa ja nopea" pätee — mutta vain oikeaan käyttötapaukseen.**
   - **Interaktiivinen, per-viesti:** kyllä. 1,5 kB viesti maskautuu ~0,3 s paikallisesti,
     laptopilla, ~4 GB muistia, ilman pilveä, ilmaiseksi. Tämä oli ennen kallista (pilvi-PII-
     palvelu tai iso malli). Nyt se on käytännössä ilmainen esisuodatin ennen LLM-kutsua.
   - **Bulkki (isot korpukset yhdellä koneella):** ei. ~2 min/MB optimoituna tarkoittaa, että
     1 GB ≈ 33 tuntia yhdellä koneella. "High-throughput on-premises" on ylimyyty
     peruslaitteistolla — bulkkiin tarvitaan GPU tai rinnakkaisuus.

## Metodologinen huomio (rehellisyys)

- Mittasin yhdellä Macilla (Apple Silicon, 16 GB), ei NVIDIA-GPU:ta. CUDA + ONNX olisi
  todennäköisesti vielä moninkertaisesti nopeampi — bulkki-tuomio koskee vain tätä luokkaa
  laitteistoa.
- Korpus on toistettua synteettistä suomidataa; tokenitiheys vastaa oikeaa tekstiä, joten
  läpäisyluvut ovat suuntaa-antavasti oikein, mutta eivät benchmarkkitarkkoja.
- Aiempi "~68 min/MB" -luku oli muistipaineen + MPS-patologian artefakti, ei mallin todellinen
  nopeus. Hyvä muistutus: mittaa vasta kun ympäristö on puhdas.
