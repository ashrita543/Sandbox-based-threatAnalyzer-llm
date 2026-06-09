"""Safe malware-like behavior for sandbox telemetry testing.

This script is intentionally non-destructive:
- Writes only to a local decoy file in the current directory.
- Spawns a harmless child process that prints text.
- Attempts an outbound connection (expected to fail in isolated sandbox).
"""

from __future__ import annotations

import os
import socket
import subprocess
import time


def write_decoy_file() -> None:
    marker_file = ".telemetry_marker.tmp"
    with open(marker_file, "a", encoding="utf-8") as f:
        f.write(f"marker ts={time.time()} pid={os.getpid()}\n")
    print(f"wrote marker file: {marker_file}")


def spawn_child() -> None:
    result = subprocess.run(
        ["sh", "-lc", "echo child-process-ran"],
        capture_output=True,
        text=True,
        check=False,
    )
    print("child stdout:", result.stdout.strip())
    print("child exit code:", result.returncode)


def attempt_network() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        # TEST-NET-1 address, safe for documentation/examples.
        s.connect(("192.0.2.1", 443))
        print("unexpected network success")
    except Exception as exc:
        print(f"network attempt failed as expected: {exc}")
    finally:
        s.close()


def main() -> None:
    write_decoy_file()
    spawn_child()
    attempt_network()


if __name__ == "__main__":
    main()
