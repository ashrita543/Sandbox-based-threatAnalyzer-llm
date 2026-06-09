"""Evaluation harness for LLM-based malware threat reports.

Usage (from repo root):
  python tools/evaluate_llm.py --examples examples --labels examples/labels.csv --output results.json

This script builds a labeled test dataset from `labels.csv`, runs each sample
through the sandbox + LLM analyzer, computes classification metrics, performs
an IOC recall check, and optionally runs a 3-run consistency check.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from sklearn.metrics import classification_report

import sys
from pathlib import Path as P

# Ensure local package imports work when running from repo root
ROOT = P(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sandboxed_script_analyzer.sandbox import run_in_sandbox
from sandboxed_script_analyzer.llm import analyze_script


def load_labels(labels_csv: str) -> Dict[str, Dict[str, Any]]:
    labels = {}
    df = pd.read_csv(labels_csv)
    for _, row in df.iterrows():
        file_val = row.get("File")
        filename = "" if pd.isna(file_val) else str(file_val).strip()
        if not filename:
            continue
        sev_val = row.get("ThreatLevel")
        type_val = row.get("Type")
        labels[filename] = {
            "true_severity": "" if pd.isna(sev_val) else str(sev_val).strip(),
            "type": "" if pd.isna(type_val) else str(type_val).strip(),
            "true_iocs": [],
        }
    return labels


def build_test_dataset(examples_dir: str, labels_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    examples = Path(examples_dir)
    dataset = []
    for p in sorted(examples.iterdir()):
        if p.is_file():
            entry = labels_map.get(p.name)
            if entry is None:
                # Skip files without labels
                continue
            dataset.append(
                {
                    "filename": p.name,
                    "filepath": str(p.resolve()),
                    "true_severity": entry["true_severity"],
                    "true_iocs": entry.get("true_iocs", []),
                }
            )
    return dataset


def ioc_recall(true_iocs: List[str], pred_iocs: List[str]) -> float:
    if not true_iocs:
        return 1.0
    true_set = set([x.lower().strip() for x in true_iocs])
    pred_set = set([x.lower().strip() for x in pred_iocs])
    if not true_set:
        return 1.0
    return len(true_set & pred_set) / len(true_set)


def evaluate_all(
    test_dataset: List[Dict[str, Any]],
    mode: str = "simple",
    model: str = "llama3.1",
) -> Dict[str, Any]:
    true_severities = []
    pred_severities = []
    ioc_recalls = []
    false_negatives = []
    false_positives = []

    for sample in test_dataset:
        print(f"Running sandbox for {sample['filename']}...")
        raw = run_in_sandbox(sample["filepath"])  # may raise
        result = analyze_script(raw, sample["filename"], mode=mode, model=model)
        report = result.get("threat_report") or {}

        true_sev = sample["true_severity"] or "UNKNOWN"
        pred_sev = (report.get("severity") or "UNKNOWN").strip()

        true_severities.append(true_sev)
        pred_severities.append(pred_sev)

        recall = ioc_recall(sample.get("true_iocs", []), report.get("indicators_of_compromise", []))
        ioc_recalls.append(recall)

        is_truly_dangerous = true_sev in ["HIGH", "CRITICAL"]
        is_predicted_dangerous = pred_sev in ["HIGH", "CRITICAL"]

        if is_truly_dangerous and not is_predicted_dangerous:
            false_negatives.append(sample["filename"])

        if not is_truly_dangerous and is_predicted_dangerous:
            false_positives.append(sample["filename"])

    severity_report = classification_report(true_severities, pred_severities, zero_division=0, output_dict=True)

    return {
        "severity_report": severity_report,
        "avg_ioc_recall": statistics.mean(ioc_recalls) if ioc_recalls else 0.0,
        "false_negatives": false_negatives,
        "false_positives": false_positives,
        "fn_rate": len(false_negatives) / len(test_dataset) if test_dataset else 0.0,
        "fp_rate": len(false_positives) / len(test_dataset) if test_dataset else 0.0,
    }


def check_consistency(
    script_path: str,
    runs: int = 3,
    mode: str = "simple",
    model: str = "llama3.1",
) -> Dict[str, Any]:
    severities = []
    for _ in range(runs):
        raw = run_in_sandbox(script_path)
        result = analyze_script(raw, Path(script_path).name, mode=mode, model=model)
        severities.append(result.get("threat_report", {}).get("severity"))
    is_consistent = len(set(severities)) == 1
    return {"severities_across_runs": severities, "consistent": is_consistent}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", default="examples", help="Path to examples directory")
    parser.add_argument("--labels", default="examples/labels.csv", help="Path to labels CSV")
    parser.add_argument("--mode", default="simple", choices=["simple", "detailed"], help="LLM report mode")
    parser.add_argument("--model", default="llama3.1", help="Ollama model name")
    parser.add_argument("--consistency-runs", type=int, default=0, help="Run N consistency checks per sample (0 to skip)")
    parser.add_argument("--output", default="evaluation_results.json", help="Output JSON file")
    args = parser.parse_args()

    labels_map = load_labels(args.labels)
    test_dataset = build_test_dataset(args.examples, labels_map)
    print(f"Loaded {len(test_dataset)} labeled samples")

    results = evaluate_all(test_dataset, mode=args.mode, model=args.model)

    if args.consistency_runs and args.consistency_runs > 0:
        consistency_summary = {}
        for sample in test_dataset:
            consistency_summary[sample["filename"]] = check_consistency(
                sample["filepath"],
                runs=args.consistency_runs,
                mode=args.mode,
                model=args.model,
            )
        results["consistency"] = consistency_summary

    # Save results
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)

    # Print a concise human-readable severity report
    print("Severity classification report (per-class F1 scores):")
    for k, v in results["severity_report"].items():
        if isinstance(v, dict):
            print(f"  {k}: f1={v.get('f1-score'):.3f} precision={v.get('precision'):.3f} recall={v.get('recall'):.3f}")

    print(f"Average IOC recall: {results['avg_ioc_recall']:.3f}")
    print(f"False negatives (missed high/critical): {results['false_negatives']}")
    print(f"False positives (benign flagged): {results['false_positives']}")
    print(f"Full results written to {args.output}")


if __name__ == "__main__":
    main()
