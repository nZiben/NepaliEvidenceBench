# NepaliEvidenceBench

NepaliEvidenceBench tests how well language models reason from Nepal public data. Questions ask models to calculate from tables, compare dated records, combine information from multiple documents, apply service rules, and recognize when the available evidence is insufficient.

**400 questions · 120 dev · 280 test · 20 domains · English, Nepali, and bilingual prompts**

Each question comes with the evidence needed to answer it, source details, and precise references to the cited records. The answer set includes expected answers, units, numeric tolerances, and calculation steps.

## Review the questions

The benchmark is a research preview. All 400 questions still need independent answer review, and Nepali wording needs native-speaker review.

Start with the [reviewer guide](REVIEW_GUIDE.md). It explains how to check a question, reproduce its answer, assess the translations, and report corrections. The complete question and answer set is in [`benchmark/items.jsonl`](benchmark/items.jsonl).

## What is included

| File | Contents |
| --- | --- |
| `benchmark/items.jsonl` | All 400 questions, evidence, expected answers, and derivations |
| `benchmark/dev.jsonl` | 120 calibration questions with answers |
| `benchmark/test.jsonl` | 280 evaluation questions without answer fields |
| `benchmark/render.py` | Creates model prompts from questions and evidence |
| `benchmark/evaluate.py` | Scores predicted answers and source citations |
| `RELEASE.json` | Version, question counts, and file checksums |

The dev and test sets use different source families. Both sets cover all eight task types: table calculation, temporal comparison, cross-document reasoning, policy plus statistics, citizen procedures, geographic reasoning, document interpretation, and insufficient evidence.

## Evaluate a model

Requires Python 3.10 or newer, with no additional packages. Run from the repository root:

```sh
# Inspect one prompt.
python3 benchmark/render.py --split dev --item-id npb-v03-0001

# Generate the evaluation prompts.
python3 benchmark/render.py --split test > prompts.jsonl

# Score responses saved in predictions.jsonl.
python3 benchmark/evaluate.py predictions.jsonl --split test
```

Send each rendered prompt to your model and save one response per line:

```json
{"item_id":"npb-v03-0001","answer":10,"citations":["E1"]}
```

Use the prompt renderer to keep expected answers out of model inputs. It includes only the selected question, its evidence, and the requested answer language. The scorer checks answer correctness and citations; unanswered questions count as incorrect. Numeric answers are checked against each question's stated tolerance.

## Limitations

The answers are public, so results may be affected by prior exposure to the dataset. The benchmark measures reasoning from supplied evidence; it does not evaluate finding documents or retrieving evidence.

Evidence excerpts are included with the questions. Full source documents are not included. Source dates and record references identify the snapshots used to construct each question; current publisher webpages may contain different information.

## Source terms

Evidence comes from Nepal public institutions. Terms and redistribution rights depend on each source. Check the publisher's terms before redistributing third-party evidence.
