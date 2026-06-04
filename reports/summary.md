# Tilannekuva - Privacy Filter vs. regex vs. hybrid (suomi)

Vertailu iteraatioittain. **Maskaus** = maskattiinko PII lainkaan (vuotosuoja);
**tyypitetty** = oikealla tyypilla (taksonomian laatu); **vuodot** = PII jai kokonaan lapi.

| Iteraatio | Esimerkkeja | Malli yksin (maskaus) | Malli yksin (vuodot) | Hybrid (tyypitetty) | Hybrid (maskaus) | Hybrid (vuodot) |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 15 | 88 % | 2 | 88 % | 94 % | 1 |
| 1 | 51 | 78 % | 11 | 96 % | 98 % | 1 |
| 2 | 45 | 67 % | 16 | 56 % | 67 % | 16 |

## Tulkinta

- Malli yksin jattaa formaaleja suomalaisia tunnisteita lapi ja ylimaskaa suomea.
- Hybridi (saannot formaaleihin + malli vapaaseen tekstiin) sulkee vuodot lahes nollaan.
- Maskaus != anonymisointi: epasuora tunnistettavuus jaa (ks. iteraatio 3).
