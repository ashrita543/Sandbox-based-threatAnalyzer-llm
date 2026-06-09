from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.sandboxed_script_analyzer import analyze_script, run_in_sandbox


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a script in the sandbox and print a threat report.")
    parser.add_argument("script", type=Path, help="Path to the Python script to analyze")
    parser.add_argument("--timeout", type=int, default=30, help="Maximum sandbox runtime in seconds")
    parser.add_argument("--image", type=str, default="sandbox-image", help="Docker image to use")
    parser.add_argument("--model", type=str, default="llama3.1", help="Ollama model to use for threat analysis")
    parser.add_argument("--mode", type=str, default="simple", choices=["simple", "detailed"], help="Report mode: simple (default) or detailed")
    args = parser.parse_args()

    # Phase 1-2: Run sandbox
    result = run_in_sandbox(str(args.script), timeout=args.timeout, image=args.image)
    
    # Phase 3-4: Analyze with behavioral summary + LLM threat report
    analysis = analyze_script(result, args.script.name, mode=args.mode)

    # Output - only print the threat report JSON to stdout for server compatibility
    # Debug info goes to stderr to avoid interfering with JSON parsing
    import sys
    print("=" * 70, file=sys.stderr)
    print(f"Phase 1-2: Sandbox Execution Result: {args.script.name}", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(json.dumps(result, indent=2), file=sys.stderr)
    
    print("\n" + "=" * 70, file=sys.stderr)
    print("Phase 3: Behavioral Summary", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(analysis["behavioral_summary"], file=sys.stderr)
    
    print("\n" + "=" * 70, file=sys.stderr)
    print(f"Phase 4: LLM-Generated Threat Report ({args.mode.upper()} MODE)", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    
    # Output only the threat report JSON to stdout for server consumption
    print(json.dumps(analysis["threat_report"], indent=2))
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
