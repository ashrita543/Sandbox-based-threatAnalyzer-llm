#!/usr/bin/env python3
"""
Generate visualizations for model performance metrics
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load the summary data
summary_path = Path("model_results/summary.json")
with open(summary_path) as f:
    data = json.load(f)

# Extract model names and metrics
models = list(data.keys())
metrics = {
    "Macro F1": [data[m]["macro_f1"] for m in models],
    "Weighted F1": [data[m]["weighted_f1"] for m in models],
    "Avg IOC Recall": [data[m]["avg_ioc_recall"] for m in models],
}

error_metrics = {
    "False Negative Rate": [data[m]["fn_rate"] for m in models],
    "False Positive Rate": [data[m]["fp_rate"] for m in models],
}

# Set up the style
plt.style.use('seaborn-v0_8-darkgrid')
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']

# === Figure 1: Model Performance Metrics ===
fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(models))
width = 0.25

for i, (metric, values) in enumerate(metrics.items()):
    ax.bar(x + (i - 1) * width, values, width, label=metric, color=colors[i])

ax.set_xlabel('Models', fontsize=12, fontweight='bold')
ax.set_ylabel('Score', fontsize=12, fontweight='bold')
ax.set_title('Model Performance Comparison - Key Metrics', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([m.replace(':', ' ') for m in models], rotation=15, ha='right')
ax.legend(loc='lower right')
ax.set_ylim(0, 1)
ax.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (metric, values) in enumerate(metrics.items()):
    for j, v in enumerate(values):
        ax.text(j + (i - 1) * width, v + 0.02, f'{v:.3f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('model_results/performance_metrics.png', dpi=300, bbox_inches='tight')
print("✓ Saved: model_results/performance_metrics.png")
plt.close()

# === Figure 2: Error Rates Comparison ===
fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(models))
width = 0.35

for i, (metric, values) in enumerate(error_metrics.items()):
    ax.bar(x + (i - 0.5) * width, values, width, label=metric, color=['#E63946', '#457B9D'][i])

ax.set_xlabel('Models', fontsize=12, fontweight='bold')
ax.set_ylabel('Error Rate', fontsize=12, fontweight='bold')
ax.set_title('Model Error Rates Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([m.replace(':', ' ') for m in models], rotation=15, ha='right')
ax.legend(loc='upper left')
ax.set_ylim(0, 0.35)
ax.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (metric, values) in enumerate(error_metrics.items()):
    for j, v in enumerate(values):
        ax.text(j + (i - 0.5) * width, v + 0.01, f'{v:.2f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('model_results/error_rates.png', dpi=300, bbox_inches='tight')
print("✓ Saved: model_results/error_rates.png")
plt.close()

# === Figure 3: Overall Score Ranking ===
fig, ax = plt.subplots(figsize=(10, 6))

# Calculate overall score (average of positive metrics, minus error rates)
overall_scores = []
for model in models:
    score = (data[model]["macro_f1"] + data[model]["weighted_f1"] + data[model]["avg_ioc_recall"]) / 3
    score -= (data[model]["fn_rate"] + data[model]["fp_rate"]) / 2
    overall_scores.append(score)

# Sort by score
sorted_indices = np.argsort(overall_scores)[::-1]
sorted_models = [models[i].replace(':', ' ') for i in sorted_indices]
sorted_scores = [overall_scores[i] for i in sorted_indices]

bars = ax.barh(sorted_models, sorted_scores, color=[colors[i] for i in sorted_indices])

ax.set_xlabel('Overall Score', fontsize=12, fontweight='bold')
ax.set_title('Model Ranking - Overall Performance', fontsize=14, fontweight='bold')
ax.set_xlim(0, 1)
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (model, score) in enumerate(zip(sorted_models, sorted_scores)):
    ax.text(score + 0.02, i, f'{score:.3f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('model_results/overall_ranking.png', dpi=300, bbox_inches='tight')
print("✓ Saved: model_results/overall_ranking.png")
plt.close()

print("\n✓ All visualizations generated successfully!")
