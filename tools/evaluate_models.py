"""Evaluate multiple Ollama models using the LLM evaluation harness.

Usage (from repo root):
  python tools/evaluate_models.py \
    --models llama3.1:latest,qwen3:4b-instruct,qwen3:4b-instruct-2507-q4_K_M \
    --examples examples \
    --labels examples/labels.csv \
    --output-dir model_results
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List

from sklearn.metrics import classification_report

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from sandboxed_script_analyzer.sandbox import run_in_sandbox
from sandboxed_script_analyzer.llm import analyze_script
from evaluate_llm import build_test_dataset, ioc_recall, load_labels


def safe_model_name(model: str) -> str:
    return "".join([c if (c.isalnum() or c in ("-", "_")) else "_" for c in model])


def init_stats() -> Dict[str, Any]:
    return {
        "true": [],
        "pred": [],
        "ioc_recalls": [],
        "false_negatives": [],
        "false_positives": [],
        "consistency": {},
    }


def evaluate_models(
    test_dataset: List[Dict[str, Any]],
    models: List[str],
    mode: str,
    consistency_runs: int,
) -> Dict[str, Dict[str, Any]]:
    per_model: Dict[str, Dict[str, Any]] = {m: init_stats() for m in models}

    for sample in test_dataset:
        print(f"Running sandbox for {sample['filename']}...")
        raw = run_in_sandbox(sample["filepath"])  # may raise

        for model in models:
            result = analyze_script(raw, sample["filename"], mode=mode, model=model)
            report = result.get("threat_report") or {}

            true_sev = sample["true_severity"] or "UNKNOWN"
            pred_sev = (report.get("severity") or "UNKNOWN").strip()

            stats = per_model[model]
            stats["true"].append(true_sev)
            stats["pred"].append(pred_sev)
            stats["ioc_recalls"].append(
                ioc_recall(sample.get("true_iocs", []), report.get("indicators_of_compromise", []))
            )

            is_truly_dangerous = true_sev in ["HIGH", "CRITICAL"]
            is_predicted_dangerous = pred_sev in ["HIGH", "CRITICAL"]

            if is_truly_dangerous and not is_predicted_dangerous:
                stats["false_negatives"].append(sample["filename"])

            if not is_truly_dangerous and is_predicted_dangerous:
                stats["false_positives"].append(sample["filename"])

        if consistency_runs > 0:
            for model in models:
                severities = []
                for _ in range(consistency_runs):
                    result = analyze_script(raw, sample["filename"], mode=mode, model=model)
                    severities.append(result.get("threat_report", {}).get("severity"))
                per_model[model]["consistency"][sample["filename"]] = {
                    "severities_across_runs": severities,
                    "consistent": len(set(severities)) == 1,
                }

    return per_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", default="examples", help="Path to examples directory")
    parser.add_argument("--labels", default="examples/labels.csv", help="Path to labels CSV")
    parser.add_argument("--mode", default="simple", choices=["simple", "detailed"], help="LLM report mode")
    parser.add_argument("--models", default="llama3.1:latest,qwen3:4b-instruct,qwen3:4b-instruct-2507-q4_K_M", help="Comma-separated model list")
    parser.add_argument("--consistency-runs", type=int, default=0, help="Run N consistency checks per sample (0 to skip)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of samples (0 = no limit)")
    parser.add_argument("--output-dir", default="model_results", help="Directory to write per-model results")
    args = parser.parse_args()

    labels_map = load_labels(args.labels)
    test_dataset = build_test_dataset(args.examples, labels_map)
    if args.limit and args.limit > 0:
        test_dataset = test_dataset[: args.limit]

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    print(f"Loaded {len(test_dataset)} labeled samples")
    print(f"Evaluating models: {models}")

    per_model = evaluate_models(test_dataset, models, mode=args.mode, consistency_runs=args.consistency_runs)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {}
    for model, stats in per_model.items():
        severity_report = classification_report(stats["true"], stats["pred"], zero_division=0, output_dict=True)
        model_results = {
            "model": model,
            "severity_report": severity_report,
            "avg_ioc_recall": statistics.mean(stats["ioc_recalls"]) if stats["ioc_recalls"] else 0.0,
            "false_negatives": stats["false_negatives"],
            "false_positives": stats["false_positives"],
            "fn_rate": len(stats["false_negatives"]) / len(test_dataset) if test_dataset else 0.0,
            "fp_rate": len(stats["false_positives"]) / len(test_dataset) if test_dataset else 0.0,
        }
        if args.consistency_runs > 0:
            model_results["consistency"] = stats["consistency"]

        safe_name = safe_model_name(model)
        out_path = output_dir / f"results_{safe_name}.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(model_results, fh, indent=2)

        summary[model] = {
            "macro_f1": severity_report.get("macro avg", {}).get("f1-score", 0.0),
            "weighted_f1": severity_report.get("weighted avg", {}).get("f1-score", 0.0),
            "avg_ioc_recall": model_results["avg_ioc_recall"],
            "fn_rate": model_results["fn_rate"],
            "fp_rate": model_results["fp_rate"],
        }

    summary_path = output_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print("Model summary (macro F1 / weighted F1):")
    for model, metrics in summary.items():
        print(
            f"  {model}: macro_f1={metrics['macro_f1']:.3f} "
            f"weighted_f1={metrics['weighted_f1']:.3f} "
            f"avg_ioc_recall={metrics['avg_ioc_recall']:.3f}"
        )
    print(f"Wrote per-model results to {output_dir}")


if __name__ == "__main__":
    main()
