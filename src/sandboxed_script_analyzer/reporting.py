from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .telemetry import format_behavioral_summary


def _format_entries(entries: list[Mapping[str, Any]], label: str) -> str:
    if not entries:
        return f"{label}: none observed."

    lines = [f"{label}: {len(entries)} event(s) observed."]
    for entry in entries[:10]:
        paths = entry.get("paths") or []
        path_text = ", ".join(paths) if paths else "no path captured"
        lines.append(f"- {entry.get('syscall')} -> {path_text} | {entry.get('result')}")
    if len(entries) > 10:
        lines.append(f"- ... {len(entries) - 10} more")
    return "\n".join(lines)


def build_threat_report(
    telemetry: Mapping[str, Any],
    stdout: str = "",
    stderr: str = "",
    script_path: str = "unknown script",
    raw_output: Mapping[str, Any] | None = None,
) -> str:
    """
    Build a threat report from telemetry.
    
    If raw_output is provided (from sandbox execution), uses Phase 3 behavioral summary.
    Otherwise falls back to raw telemetry formatting.
    """
    # Phase 3: Use behavioral summary if raw_output available
    if raw_output:
        behavioral_summary = format_behavioral_summary(dict(raw_output))
        report_lines = [
            f"=== Threat Report: {script_path} ===",
            "",
            "--- Behavioral Fingerprint (Phase 3) ---",
            behavioral_summary,
        ]
        return "\n".join(report_lines)
    
    # Fallback: Raw telemetry formatting
    file_changes = list(telemetry.get("file_changes", []))
    process_activity = list(telemetry.get("process_activity", []))
    network_attempts = list(telemetry.get("network_attempts", []))

    report_lines = [
        f"Threat report for {script_path}",
        "",
        _format_entries(file_changes, "File changes"),
        "",
        _format_entries(process_activity, "Process activity"),
        "",
        _format_entries(network_attempts, "Network attempts"),
    ]

    if stdout.strip():
        report_lines.extend([
            "",
            "Sandbox stdout excerpt:",
            stdout.strip()[:2000],
        ])

    if stderr.strip():
        report_lines.extend([
            "",
            "Sandbox stderr excerpt:",
            stderr.strip()[:2000],
        ])

    return "\n".join(report_lines)
