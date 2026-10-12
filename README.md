# NepaliEvidenceBench

An open benchmark for evidence-grounded reasoning over frozen Nepal public data. This repository publishes the unchanged **NepaliBench v0.3-open** dataset under a distinct repository name.

**400 questions · 120 dev · 280 test · 20 domains · English, Nepali, and bilingual prompts**

Tasks cover table calculations, temporal comparisons, cross-document joins, policy plus statistics, citizen procedures, geographic reasoning, document interpretation, and insufficient evidence. Each item includes materialized evidence with source provenance and exact locators. The gold master additionally includes typed answers and deterministic derivations.

## For reviewers

Start with [REVIEW_GUIDE.md](REVIEW_GUIDE.md). Review the gold master in `benchmark/items.jsonl`. Each record has English and Nepali questions, evidence, expected answers, derivations, and review status. The dataset has been machine-validated; **all 400 items still require independent human review**. Nepali and bilingual wording also needs native-speaker review.

## Files

- `benchmark/items.jsonl`: all 400 items, with gold answers and derivations.
- `benchmark/dev.jsonl`: 120 calibration items with gold answers.
- `benchmark/test.jsonl`: 280 items without answers or derivations.
- `benchmark/render.py`: canonical prompt renderer.
- `benchmark/evaluate.py`: answer and source-citation scorer.
- `benchmark/original_manifest.json`: original release manifest, preserved unchanged.
- `RELEASE.json`: export provenance and checksums of the files published here.

The split is grouped by source family. Both partitions cover all eight task families. Source families do not overlap between dev and test. The original item IDs and version identifiers are preserved.

## Run

Python 3.10 or newer; no third-party packages required. From the repository root:

```sh
python3 benchmark/render.py --split dev --item-id npb-v03-0001
python3 benchmark/render.py --split test > prompts.jsonl
python3 benchmark/evaluate.py predictions.jsonl --split test
```

Return one prediction per line:

```json
{"item_id":"npb-v03-0001","answer":10,"citations":["E1"]}
```

Use the renderer for model evaluation: it exposes the selected question and evidence without gold answers or alternate translations. Missing predictions count as incorrect. Numeric scoring uses each item's declared absolute tolerance. Citation scoring measures source compliance over supplied evidence.

## Scope and limitations

This is an open diagnostic research preview. The gold answers are public, so the test split is not contamination-resistant. The benchmark tests reasoning over supplied oracle evidence, rather than retrieval from the full corpus. No model performance results or completed human reviews are claimed.

This repository includes only the benchmark and its review/evaluation materials. Original corpus downloads, normalized source files, collection code, and corpus reports are outside this export. Evidence excerpts and provenance remain embedded in the items. Consequently, the original corpus-dependent builder and validator are not bundled. The original manifest references those upstream files; `RELEASE.json` records the standalone export.

## Source terms

Evidence derives from Nepal public institutions. Source terms and redistribution rights remain source-specific. This repository does not assign a blanket license to third-party evidence. Review source-specific terms before further redistribution.
