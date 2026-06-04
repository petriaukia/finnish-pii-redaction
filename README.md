# Finnish PII redaction: OpenAI Privacy Filter vs. regex vs. hybrid

An iterative test harness that measures how well [OpenAI Privacy
Filter](https://huggingface.co/openai/privacy-filter) detects personal data in
**Finnish** text, compared against a rule-based regex layer and a hybrid of the two —
plus throughput and memory benchmarks on commodity hardware.

The goal is not to prove "GDPR compliance". It is to find out, practically, where a
small specialised PII model helps, where deterministic rules are simply better, where
neither is enough, and whether it is fast and light enough to put into a service.

## Verdict (so far)

Interesting exercise, **not** a production solution for Finnish today:

- **Language-blind.** It leaks ~30 % of inflected Finnish names and addresses, mislabels
  the Finnish personal identity code as a bank account number, and misreads common Finnish
  words (`Henkilötunnus`, `Helsingissä`) as person names. It is strongly English-centric.
- **Slow on the obvious path.** The model-card example plus `device="mps"` gives ~54 min
  per MB (and MPS is *slower* than CPU here). The optimised quantized-ONNX path is ~8×
  faster but still ~2 min/MB — fine for interactive per-message use, too slow for bulk.
- **Memory-hungry.** ~3.4–3.9 GB resident.

Where it *does* earn a place: as a fast local **fallback** for unstructured PII (names,
addresses) behind a rules layer, and as a **positive canary** in testing — but only on the
optimised runtime, and never as a control or a sign-off. "Works in all languages" is
written from the center; a small European language is the edge case the training data
barely saw.

## Accuracy findings (preliminary, small synthetic sets)

| Iteration | Examples | Model alone (redacted) | Model alone (leaks) | Hybrid (typed) | Hybrid (redacted) | Hybrid (leaks) |
|---|---:|---:|---:|---:|---:|---:|
| 0 (smoke) | 15 | 88 % | 2 | 88 % | 94 % | 1 |
| 1 (formal identifiers) | 51 | 78 % | 11 | 98 % | 98 % | 1 |
| 2 (names & addresses) | 45 | 71 % | 14 | 62 % | 71 % | 14 |

In iteration 2 the hybrid equals the model alone, because regex scores **0 %** on
names/addresses — there the model is the only layer that works, and it leaks ~30 %.

Two metrics, because they answer different questions:

- **Redaction recall** — was the PII text masked at all (by any label)? This is leak
  protection. If the model tags a Finnish SSN as `account_number`, the data still does
  not leak, even though the label is wrong.
- **Typed recall** — was it masked with the *correct* category? This is taxonomy quality.

### What the data shows

1. **Don't reach for a model when the format is set in stone.** Privacy Filter has no
   category for the Finnish personal identity code (`henkilötunnus`) or IP addresses. It
   labelled an SSN as `account_number`, an IP as `private_url`, and missed a Finnish IBAN
   entirely. A few lines of regex catch all of these at ~100 %. Rules for structured
   identifiers, model for unstructured text — never confuse the two roles.
2. **This is not a GDPR magic wand** — as OpenAI states on the model card ("not a
   complete anonymization solution"). Removing classical PII is not anonymization:
   indirect identifiability remains (e.g. *"the municipality's only Swedish-speaking
   special-needs teacher went on sick leave in February 2025"* — zero classical PII,
   still identifiable). Iteration 3 (contextual) is defined as data but not yet auto-scored.
3. **The model's honest place** is the *unstructured-coverage* layer (names, addresses,
   free text — where regex scores 0 %), inside a defence-in-depth stack of rules + model +
   human/process. As verification it only works as a **positive canary**: if a cheap model
   *still* finds PII in supposedly-clean production output, your real redactor has a bug.
   Never treat the model's silence as a sign-off — it missed 11 identifiers in iteration 1.

## Performance (throughput & memory)

Measured on Apple Silicon, 16 GB RAM, no NVIDIA GPU. Full write-up:
[reports/benchmark.md](reports/benchmark.md).

| Path | time / 1 MB | peak RSS |
|---|---:|---:|
| `transformers` fp32, **MPS** (model-card default) | ~54 min | — |
| `transformers` fp32, CPU | ~15.5 min | 3.4 GB |
| ONNX int8/q4, CPU | ~3.5 min | 3.9 GB |
| **ONNX int8, CPU, batch=32** | **~2.0 min** | 3.9 GB |

Per-message latency (1.5 kB message, several PII items, ONNX int8): **315 ms** — negligible
as a fallback before a 1–10 s LLM call. Note MPS is a trap for this model (MoE ops fall back
to CPU); on Apple Silicon, use **CPU**, and the **quantized ONNX** weights (`onnx/`) for
throughput, not the default pipeline.

## How it runs

OpenAI Privacy Filter is **not** a chat/LLM model — it is a 1.5B-parameter
token-classification (NER) model. It runs in-process via the HuggingFace `transformers`
pipeline (`token-classification`, `aggregation_strategy="simple"`). No server, no Ollama,
no cloud. Weights download from the HF hub on first run.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Verify the model loads and detects spans
.venv/bin/python scripts/run_privacy_filter.py --self-test

# Run iterations (Privacy Filter / regex / hybrid) and write reports
.venv/bin/python scripts/eval.py --data data/iteration_0_smoke.jsonl --iter 0
.venv/bin/python scripts/eval.py --data data/iteration_1_formal_identifiers.jsonl --iter 1
.venv/bin/python scripts/eval.py --data data/iteration_2_names_addresses.jsonl --iter 2

# Aggregate iterations into a single overview
.venv/bin/python scripts/summary.py --iters 0 1 2

# Throughput + memory benchmark
.venv/bin/python scripts/benchmark.py --mb 1.0
```

Results land in `results/iteration_<n>/`, reports in `reports/` (incl.
[summary.md](reports/summary.md) and [benchmark.md](reports/benchmark.md)).

## Tests

The suite is **offline** — it never loads the model (pure functions plus a monkeypatched
pipeline), so it runs in well under a second and needs only `pytest`:

```bash
.venv/bin/pip install pytest
.venv/bin/pytest
```

## Layout

```
type_mapping.py            # model's 8 categories <-> test-plan types
scripts/
  run_privacy_filter.py    # transformers token-classification, in-process
  run_regex_baseline.py    # Finnish regexes (SSN, IP, FI-IBAN, email, phone, ...)
  run_hybrid.py            # union of model + regex spans (regex wins on formal IDs)
  evaluate_spans.py        # typed vs redaction recall, leaks, mislabels, false positives
  report.py                # per-iteration markdown report
  summary.py               # cross-iteration overview
  benchmark.py             # throughput + memory benchmark
  eval.py                  # CLI tying it together
data/                      # JSONL datasets (Finnish examples)
tests/                     # offline pytest suite
```

The full test plan (in Finnish) is in
[privacy-filter-suomi-testisuunnitelma.md](privacy-filter-suomi-testisuunnitelma.md).

## License

Apache 2.0 — same as the model. See [LICENSE](LICENSE).
