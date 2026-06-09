# Sandboxed Script Analyzer 

A lightweight, local-first security tool designed to safely execute and analyze untrusted Python scripts inside a hardened Docker sandbox. It captures low-level system call telemetry (`strace`), tracks runtime filesystem mutations, and generates compact behavioral fingerprints optimized for automated triage or local LLM analysis.

## 🌟 Key Features

* 📦 **Hardened Isolation:** Executes target scripts in a strictly non-root, read-only Docker container containerized environment.
* 🔍 **System Telemetry:** Captures and parses raw `strace` logs to track hidden file access, process spawning, and socket creation.
* 💾 **Filesystem Diff Tracking:** Computes before-and-after snapshots to capture unauthorized file creations, modifications, or deletion attempts.
* 🧠 **Local AI Triage:** Seamlessly hooks into local LLMs (via Ollama) to convert complex system logs into high-level threat assessments without data leaks.
* 🔌 **Zero External Dependencies:** Built for air-gapped or privacy-focused operations; your telemetry never leaves your machine.

---

## 🏗️ Project Structure

```text
├── sandbox/                            # Hardened Docker environment definitions
├── examples/                           # Built-in simulation scripts for validation
├── main.py                             # CLI orchestrator & entrypoint
└── src/sandboxed_script_analyzer/
    ├── sandbox.py                      # Container lifecycles & volume orchestration
    ├── telemetry.py                    # Strace parsing engine & heuristic extractors
    ├── reporting.py                    # Forensic summary & fingerprint formatting
    └── llm.py                          # Local LLM engineering & prompt contexts

```

---

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have [Docker](https://docs.docker.com/get-docker/) installed and running locally.

### 2. Installation

Clone the repository and build the hardened sandbox image:

```bash
# Build the containment image
docker build -t sandbox-image ./sandbox

# Set up the host analysis environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

### 3. Run Your First Analysis

Execute a quick triage on a built-in simulation script:

```bash
python main.py examples/malicious_read_passwd.py

```

---

## ⚙️ Advanced Usage & AI Triage

You can feed behavioral summaries into a local LLM to generate structured, human-readable threat incident reports.

> [!NOTE]
> AI Triage is entirely optional. The core telemetry engine runs 100% offline without requiring an LLM.

```bash
# 1. Spin up your local model via Ollama
ollama run deepseek-r1:14b

# 2. Run the analyzer with detailed AI reporting
python main.py examples/malicious_read_passwd.py --mode detailed --model deepseek-r1:14b

```

### Behavioral Validation Suite

The `examples/` directory contains pre-configured test vectors to validate detection heuristics:

* **`malicious_read_passwd.py`** — Simulates credential harvesting via unauthorized `/etc/passwd` reads.
* **`malicious_spawn_process.py`** — Simulates reverse-shell behaviors by spawning unexpected background subprocesses.
* **`malicious_network_attempt.py`** — Simulates data exfiltration via unauthorized outbound socket connections.

---

## 🛡️ Hardening & Security Profile

> [!WARNING]
> While this engine enforces rigid containment guardrails, executing untrusted code always carries inherent risk (e.g., kernel-level exploits). Ensure your host Docker daemon is kept updated.

| Security Layer | Mechanism | Purpose |
| --- | --- | --- |
| **User Privileges** | `sandboxuser` (Non-Root) | Prevents container escape via root privilege abuse. |
| **Storage Security** | Read-Only Rootfs | Mitigates persistent container contamination. |
| **Lifecycle** | Forced `finally` cleanup | Ensures aggressive container destruction (`rm`) post-execution. |
| **Data Privacy** | Local Execution Loop | Air-gaps telemetry; zero third-party API exposure. |
