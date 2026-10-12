#!/usr/bin/env python3
"""Score NepaliBench answers and source citations against the local gold set."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEVANAGARI = str.maketrans("०१२३४५६७८९", "0123456789")


def load_jsonl(source: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value)).casefold().strip()
    return re.sub(r"\s+", " ", text).strip(" .")


def numeric(value: object) -> Decimal:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        result = Decimal(str(value))
        if not result.is_finite():
            raise ValueError
        return result
    text = unicodedata.normalize("NFKC", str(value)).translate(DEVANAGARI).replace("\u00a0", " ")
    text = re.sub(r"(?<=\d)[,\s]+(?=\d)", "", text)
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)", text.strip()):
        raise ValueError
    return Decimal(text.strip())


def score(prediction: object, gold: dict[str, object]) -> bool | None:
    kind, expected = gold["type"], gold["value"]
    if kind == "number":
        try:
            return abs(numeric(prediction) - Decimal(str(expected))) <= Decimal(str(gold.get("tolerance", 0)))
        except (InvalidOperation, TypeError, ValueError):
            return False
    if kind == "boolean":
        if isinstance(prediction, bool):
            return prediction is expected
        values = {"true": True, "yes": True, "हो": True, "false": False, "no": False, "होइन": False}
        return values.get(normalize(prediction)) is expected
    if kind == "set":
        values = prediction if isinstance(prediction, list) else str(prediction).split(",")
        return {normalize(value) for value in values} == {normalize(value) for value in expected}
    if kind == "unanswerable":
        return normalize(prediction) in {
            "unanswerable", "cannot be determined", "insufficient information", "अपर्याप्त जानकारी"
        }
    if kind in {"entity", "date", "text"}:
        return normalize(prediction) == normalize(expected)
    return None


def cited_sources(prediction: dict[str, object], item: dict[str, object]) -> set[str]:
    lookup = {}
    for evidence in item["evidence"]:
        lookup[evidence["evidence_id"]] = evidence["source_id"]
        lookup[evidence["source_id"]] = evidence["source_id"]
        lookup[evidence["artifact"]] = evidence["source_id"]
    citations = prediction.get("citations", [])
    if not isinstance(citations, list):
        return set()
    return {
        lookup.get(citation, f"unknown:{citation}")
        for citation in citations
        if isinstance(citation, str)
    }


def summarize(records: list[dict[str, object]]) -> dict[str, object]:
    answer_correct = sum(record["answer_correct"] is True for record in records)
    expected = sum(len(record["expected_sources"]) for record in records)
    provided = sum(len(record["provided_sources"]) for record in records)
    matched = sum(len(record["expected_sources"] & record["provided_sources"]) for record in records)
    precision = matched / provided if provided else 0.0
    recall = matched / expected if expected else 0.0
    exact = sum(record["expected_sources"] == record["provided_sources"] for record in records)
    return {
        "items": len(records),
        "answer_accuracy": answer_correct / len(records) if records else None,
        "citation_precision": precision,
        "citation_recall": recall,
        "citation_f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "citation_exact_match": exact / len(records) if records else None,
        "joint_accuracy": sum(
            record["answer_correct"] is True and record["expected_sources"] == record["provided_sources"]
            for record in records
        ) / len(records) if records else None,
    }


def sliced(records: list[dict[str, object]], field: str) -> dict[str, dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        values = record["item"][field]
        if not isinstance(values, list):
            values = [values]
        for value in values:
            groups[value].append(record)
    return {value: summarize(values) for value, values in sorted(groups.items())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path, help="JSONL with item_id, answer, and citations fields")
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    args = parser.parse_args()

    gold_items = [item for item in load_jsonl(HERE / "items.jsonl") if item["split"] == args.split]
    predictions = load_jsonl(args.predictions)
    if any(not isinstance(row, dict) for row in predictions):
        raise SystemExit("every prediction must be a JSON object")
    if any(not isinstance(row.get("item_id"), str) or not row["item_id"] for row in predictions):
        raise SystemExit("every prediction needs a non-empty string item_id")
    if any("answer" not in row or "citations" not in row for row in predictions):
        raise SystemExit("every prediction needs answer and citations fields")
    if any(
        not isinstance(row["citations"], list) or not all(isinstance(value, str) for value in row["citations"])
        for row in predictions
    ):
        raise SystemExit("citations must be a JSON array of strings")
    by_id = {row["item_id"]: row for row in predictions}
    if len(by_id) != len(predictions):
        raise SystemExit("duplicate item_id in predictions")

    records = []
    manual_review = []
    for item in gold_items:
        prediction = by_id.get(item["item_id"], {})
        outcome = score(prediction.get("answer"), item["answer"]) if "answer" in prediction else False
        if outcome is None:
            manual_review.append(item["item_id"])
        records.append({
            "item": item,
            "answer_correct": outcome,
            "expected_sources": {entry["source_id"] for entry in item["evidence"]},
            "provided_sources": cited_sources(prediction, item),
        })

    known = {item["item_id"] for item in gold_items}
    report = {
        "version": gold_items[0]["version"] if gold_items else None,
        "split": args.split,
        "predictions_received": len(predictions),
        "predictions_scored": len(known & set(by_id)),
        "overall": summarize(records),
        "by_task": sliced(records, "task_family"),
        "by_domain": sliced(records, "domains"),
        "by_language": sliced(records, "language"),
        "by_difficulty": sliced(records, "difficulty"),
        "manual_review": manual_review,
        "missing_prediction_ids": sorted(known - set(by_id)),
        "unknown_prediction_ids": sorted(set(by_id) - known),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
