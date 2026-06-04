# Finnish PII redaction: OpenAI Privacy Filter vs. regex vs. hybrid

An iterative test harness that measures how well [OpenAI Privacy
Filter](https://huggingface.co/openai/privacy-filter) detects personal data in
**Finnish** text, compared against a rule-based regex layer and a hybrid of the two.

The goal is not to prove "GDPR compliance". It is to find out, practically, where a
small specialised PII model helps, where deterministic rules are simply better, and
where neither is enough.

## TL;DR findings (preliminary, small synthetic sets)

| Iteration | Examples | Model alone (redacted) | Model alone (leaks) | Hybrid (typed) | Hybrid (redacted) | Hybrid (leaks) |
|---|---:|---:|---:|---:|---:|---:|
| 0 (smoke) | 15 | 88 % | 2 | 88 % | 94 % | 1 |
| 1 (formal identifiers) | 51 | 78 % | 11 | 98 % | 98 % | 1 |

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
   still identifiable). See iteration 3.
3. **The model's honest place in an architecture** is the *unstructured-coverage* layer
   (names, addresses, free text — where regex scores 0 %), inside a defence-in-depth stack
   of rules + model + human/process. As a verification step it only works as a **positive
   canary**: if a cheap model *still* finds PII in supposedly-clean production output, your
   real redactor has a bug. Never treat the model's silence as a sign-off — it missed 11
   identifiers in iteration 1.

The model is also strongly English-centric, so it over-redacts Finnish: common Finnish
words (`Henkilötunnus`, `Tilinumero`, `Helsingissä`) get flagged as person names. For
privacy that is a tolerable false positive; for usability it is a real cost.

## How it runs

OpenAI Privacy Filter is **not** a chat/LLM model — it is a 1.5B-parameter
token-classification (NER) model. It runs in-process via the HuggingFace `transformers`
pipeline (`token-classification`, `aggregation_strategy="simple"`), on Apple Silicon
(`mps`), CUDA, or CPU. No server, no Ollama, no cloud. Weights download from the HF hub on
first run.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Verify the model loads and detects spans
.venv/bin/python scripts/run_privacy_filter.py --self-test

# Run one iteration (Privacy Filter / regex / hybrid) and write a report
.venv/bin/python scripts/eval.py --data data/iteration_0_smoke.jsonl --iter 0
.venv/bin/python scripts/eval.py --data data/iteration_1_formal_identifiers.jsonl --iter 1

# Aggregate iterations into a single overview
.venv/bin/python scripts/summary.py --iters 0 1
```

Results land in `results/iteration_<n>/`, reports in `reports/`.

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
  eval.py                  # CLI tying it together
data/                      # JSONL datasets (Finnish examples)
tests/                     # offline pytest suite
```

The full test plan (in Finnish) is in
[privacy-filter-suomi-testisuunnitelma.md](privacy-filter-suomi-testisuunnitelma.md).

## License

Apache 2.0 — same as the model. See [LICENSE](LICENSE).
