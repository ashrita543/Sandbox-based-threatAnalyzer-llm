"""Phase 4 — LLM-based threat report generation."""

from __future__ import annotations

import json
from typing import Any

import ollama


SYSTEM_PROMPT = """
You are a senior malware analyst at a cybersecurity firm.

You will be given a behavioral log from a script that was executed inside an
isolated sandbox. The log contains file system changes, spawned processes,
syscall activity, and network connection attempts.

Your job is to analyze this log and produce a structured threat report.

Always respond in the following JSON format:
{
  "threat_name": "short name for what this appears to be (e.g. Reverse Shell, Data Exfiltration, Ransomware Dropper)",
  "severity": "one of: No Threat / LOW / MEDIUM / HIGH / CRITICAL",
  "summary": "2-3 sentence plain English explanation of what this script did and why it is or isn't dangerous",
  "indicators_of_compromise": ["list", "of", "specific", "suspicious", "findings"],
  "likely_intent": "what the attacker was trying to accomplish",
  "recommended_action": "what the user should do now (e.g. isolate machine, full scan, safe to ignore)"
}

Rules:
- Be concise. No padding or filler.
- Base your analysis strictly on the behavioral log provided. Do not invent findings.
- If the behavior looks benign, say so clearly and set severity to LOW.
- Use plain language. The report may be read by non-experts.
"""

SYSTEM_PROMPT_DETAILED = """
You are a senior malware analyst at a cybersecurity firm writing a full technical
incident report. You will be given a behavioral log from a script executed inside
an isolated sandbox containing file system changes, spawned processes, syscall
activity, and network connection attempts.

Always respond in the following JSON format:
{
  "threat_name": "specific name for this threat (e.g. Python-based Reverse Shell with Credential Harvesting)",
  "severity": "one of: No Threat / LOW / MEDIUM / HIGH / CRITICAL",
  "severity_justification": "1-2 sentences explaining exactly why you assigned this severity level",
  "malware_category": "one or more of: Ransomware / Spyware / Trojan / Worm / Rootkit / Dropper / Backdoor / Cryptominer / Infostealer / Reverse Shell / Benign",
  "executive_summary": "3-4 sentence non-technical overview of what this script does and its danger level. Written for a manager, not an engineer.",
  "technical_analysis": {
    "filesystem_behavior": "Detailed explanation of every file the script touched, created, or deleted and what each action suggests about intent",
    "process_behavior": "Detailed explanation of every process spawned, what that process is normally used for, and why spawning it here is suspicious or benign",
    "network_behavior": "Detailed explanation of every network attempt — IPs contacted, ports used, protocols, and what the attacker likely intended with each connection",
    "syscall_patterns": "Patterns in the syscall log that reveal the script's technique (e.g. repeated openat on credential files suggests enumeration)"
  },
  "attack_chain": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "indicators_of_compromise": {
    "files": ["list of suspicious file paths"],
    "processes": ["list of suspicious process names"],
    "network": ["list of IPs, domains, ports"],
    "behavioral": ["list of suspicious behavioral patterns e.g. reads /etc/passwd then opens outbound socket"]
  },
  "mitre_attack_techniques": [
    "TA0001 - Initial Access: ...",
    "TA0002 - Execution: ...",
    "TA0010 - Exfiltration: ..."
  ],
  "likely_intent": "Detailed explanation of what the attacker was trying to accomplish and what a successful attack would have looked like",
  "false_positive_assessment": "Honest assessment of whether this could be legitimate software behaving unusually. State your confidence level.",
  "recommended_action": {
    "immediate": "What to do right now",
    "short_term": "What to do in the next 24-48 hours",
    "long_term": "Systemic changes to prevent this class of attack"
  }
}

Rules:
- Every field must be populated. Never return null or empty strings.
- Base your analysis strictly on the behavioral log. Do not invent findings.
- The attack_chain must tell a coherent story — each step must follow logically from the previous.
- MITRE ATT&CK techniques must be real technique IDs. Only include ones actually evidenced by the log.
- If behavior is benign, still complete every field — explain why each signal is non-threatening.
- technical_analysis fields should be 2-4 sentences each, specific to this log.
"""


def build_user_message(behavioral_summary: str, script_filename: str) -> str:
    """Build the user message for the LLM with behavioral summary."""
    return f"""
Analyze the following sandbox execution log for the script: `{script_filename}`

{behavioral_summary}

Produce the threat report now.
"""


def generate_threat_report(
    behavioral_summary: str,
    script_filename: str,
    model: str = "deepseek-r1:14b",
    mode: str = "simple",
) -> dict[str, Any]:
    """
    Call the local ollama model to generate a threat report.
    
    Args:
        behavioral_summary: Output from format_behavioral_summary (Phase 3)
        script_filename: Name of the script being analyzed
        model: Ollama model name (default: llama3.1)
        mode: Report mode - "simple" (default) or "detailed"
    
    Returns:
        Parsed JSON threat report from the LLM
    """
    user_message = build_user_message(behavioral_summary, script_filename)
    system_prompt = SYSTEM_PROMPT_DETAILED if mode == "detailed" else SYSTEM_PROMPT
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )
        
        # Extract the response text
        response_text = response.get("message", {}).get("content", "").strip()
        
        # Try to parse as JSON
        # The LLM might include markdown code blocks, so extract JSON if needed
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        threat_report = json.loads(response_text)
        return threat_report
        
    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails
        return {
            "threat_name": "Analysis Error",
            "severity": "UNKNOWN",
            "summary": f"Failed to parse LLM response: {str(e)}",
            "indicators_of_compromise": [],
            "likely_intent": "unknown",
            "recommended_action": "review raw behavioral summary manually",
        }
    except Exception as e:
        # Catch ollama connection errors, etc.
        return {
            "threat_name": "LLM Connection Error",
            "severity": "UNKNOWN",
            "summary": f"Could not reach LLM service: {str(e)}",
            "indicators_of_compromise": [],
            "likely_intent": "unknown",
            "recommended_action": "ensure ollama is running",
        }


def analyze_script(
    raw_sandbox_output: dict[str, Any],
    script_filename: str,
    mode: str = "simple",
    model: str = "llama3.1",
) -> dict[str, Any]:
    """
    Complete analysis pipeline: Phase 3 (behavioral summary) + Phase 4 (LLM threat report).
    
    Args:
        raw_sandbox_output: Output from run_in_sandbox
        script_filename: Name of the script being analyzed
        mode: Report mode - "simple" (default) or "detailed"
    
    Returns:
        Dictionary with behavioral_summary and threat_report
    """
    from .telemetry import format_behavioral_summary
    
    # Phase 3: Format behavioral summary
    behavioral_summary = format_behavioral_summary(raw_sandbox_output)

    # Phase 4: Generate threat report via LLM
    threat_report = generate_threat_report(
        behavioral_summary,
        script_filename,
        model=model,
        mode=mode,
    )
    
    return {
        "behavioral_summary": behavioral_summary,
        "threat_report": threat_report,
    }
