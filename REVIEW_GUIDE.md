# Reviewer guide

## Goal

Determine whether each question is clear, its evidence sufficient, and its gold answer correct. Check English and Nepali formulations for equivalent meaning, including numbers, units, dates, conditions, and entities. Reviewers should be fluent in the language they assess; consequential domain questions should also receive appropriate domain review.

## Find an item

Use `benchmark/items.jsonl`: UTF-8 JSON Lines, one question per line. Search by `item_id`. Each record includes `question`, `question_en`, `question_ne`, `answer`, `derivation`, `evidence`, and review metadata. Do not assume a stored answer or derivation is correct merely because it passed machine validation.

## Review steps

1. Read the selected question and both translations. Check that the expected answer language is appropriate.
2. Read the embedded `evidence[].content`. Each evidence block has an ID, source title, institution, retrieval date, source SHA-256, artifact path, and locator. CSV record numbers are one-based and include the header as record 1; row ranges are inclusive.
3. Independently derive the answer from the evidence before comparing it with the gold answer. Check operand selection, calculation, rounding, tolerance, units, dates/calendar notation, and entity spelling.
4. Compare your calculation with `answer` and `derivation`. The latter describes intended operations but is not independent evidence.
5. Check whether the evidence supports every required step. Mark insufficient, conflicting, or ambiguous evidence explicitly. For an unanswerable item, verify that abstention is justified.
6. Where necessary, inspect the publisher's original source. This standalone repository does not include full corpus files. The original `artifact` path is a provenance locator, not a working link in this repository. Record when the full frozen source cannot be independently checked; a current webpage may differ from its recorded snapshot.
7. Record a decision and concrete notes. Do not overwrite the released JSONL files during initial review.

## Submit feedback

Open a GitHub issue titled `Review: <item_id>` (batch issues are acceptable if every item has its own result), or send the same information to the project maintainer. Include:

- Item ID and reviewer identifier.
- Review scope: answer/evidence, English wording, Nepali wording, or domain review.
- Decision: `accept`, `needs_changes`, or `cannot_verify`.
- Independently derived answer and calculation or evidence locator.
- Error or ambiguity found, with a proposed correction when possible.
- Whether only embedded evidence or also the full source was checked.
- Remaining uncertainties.

Two independent answer reviews are the target for every item. Native-speaker review should cover every Nepali/bilingual prompt. Accept an item only within the scope you actually checked. Do not record another person's review as your own.

## Common problems to flag

Wrong row/column selection; incompatible snapshots; calendar or unit confusion; gold answers not entailed by evidence; translation changes to meaning; missing conditions in service rules; multiple plausible answers; inappropriate numeric tolerance; unsupported geographic joins; evidence that accidentally reveals a direct answer where reasoning is intended.

All items initially retain their original `machine_validated_needs_human_review` status. Feedback is a review record, not an automatic approval or a change to the release.
