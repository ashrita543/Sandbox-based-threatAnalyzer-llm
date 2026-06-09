from __future__ import annotations

from dataclasses import asdict, dataclass
import subprocess
from pathlib import Path
from typing import Any

import docker
from docker.errors import DockerException

from .telemetry import parse_strace_trace


@dataclass(frozen=True)
class SandboxResult:
    status: str
    stdout: str
    stderr: str
    strace_log: str
    fs_diff: dict[str, list[str]]
    network_hits: list[str]
    exit_code: int | None
    timed_out: bool
    telemetry: dict[str, Any]
    filesystem_diff: dict[str, list[str]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_container_file(container_id: str, file_path: str) -> str:
    result = subprocess.run(
        ["docker", "exec", "--user", "sandboxuser", container_id, "sh", "-lc", f"cat {file_path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def snapshot_filesystem(container_id: str) -> set[str]:
    """Get all file paths currently in the container."""
    find_expr = (
        "find / "
        "\\( -path /proc -o -path /proc/* -o -path /sys -o -path /sys/* "
        "-o -path /tmp/strace.log -o -path /tmp/stdout.log -o -path /tmp/stderr.log \\) -prune "
        "-o -type f -print"
    )
    result = subprocess.run(
        ["docker", "exec", "--user", "sandboxuser", container_id, "sh", "-lc", find_expr],
        capture_output=True,
        text=True,
        check=False,
    )
    paths = [line for line in result.stdout.splitlines() if line.strip()]
    return set(paths)


def diff_filesystem(before: set[str], after: set[str]) -> dict[str, list[str]]:
    return {
        "created": sorted(after - before),
        "deleted": sorted(before - after),
    }


def _build_network_hits(telemetry: dict[str, Any]) -> list[str]:
    network_attempts = telemetry.get("network_attempts", [])
    hits: list[str] = []
    for event in network_attempts:
        syscall = str(event.get("syscall", "unknown"))
        arguments = str(event.get("arguments", "")).strip()
        result = str(event.get("result", "")).strip()
        hits.append(f"{syscall}({arguments}) = {result}".strip())
    return hits


def run_in_sandbox(script_path: str, timeout: int = 30, image: str = "sandbox-image") -> dict[str, Any]:
    script = Path(script_path).expanduser().resolve()
    if not script.is_file():
        raise FileNotFoundError(f"Script not found: {script}")

    client = docker.from_env()

    stdout_path = "/tmp/stdout.log"
    stderr_path = "/tmp/stderr.log"
    trace_path = "/tmp/strace.log"

    keep_alive_command = ["sh", "-lc", "while true; do sleep 1; done"]

    # Mount the script using its original filename inside the container so
    # shell scripts and other extension-based runtimes can be executed.
    container_script_path = f"/sandbox/{script.name}"

    # Choose a runtime command based on file extension. Defaults to Python
    # for `.py` files and `sh` for shell scripts. This keeps the sandbox
    # flexible for simple non-Python artifacts used for testing.
    suffix = script.suffix.lower()
    if suffix == ".sh":
        interpreter_cmd = f"sh {container_script_path}"
    else:
        # default: run with python
        interpreter_cmd = f"python {container_script_path}"

    run_command = (
        f"strace -f -e trace=file,process,network -o {trace_path} "
        f"{interpreter_cmd} > {stdout_path} 2> {stderr_path}"
    )

    container = None
    timed_out = False
    exit_code: int | None = None
    filesystem_diff: dict[str, list[str]] = {"created": [], "deleted": []}
    status = "error"
    runtime_error = ""
    stdout = ""
    stderr = ""
    strace_log = ""

    try:
        container = client.containers.create(
            image=image,
            command=keep_alive_command,
            volumes={
                str(script): {
                    "bind": container_script_path,
                    "mode": "ro",
                },
            },
            user="sandboxuser",
            network_mode="none",
            mem_limit="128m",
            cpu_period=100000,
            cpu_quota=50000,
            working_dir="/sandbox",
            environment={
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONUNBUFFERED": "1",
            },
            tty=False,
            detach=True,
        )
        container.start()

        before_snapshot = snapshot_filesystem(container.id)
        try:
            exec_result = subprocess.run(
                ["docker", "exec", "--user", "sandboxuser", container.id, "sh", "-lc", run_command],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            exit_code = exec_result.returncode
            status = "completed"
        except subprocess.TimeoutExpired:
            timed_out = True
            exit_code = None
            status = "timeout"

        after_snapshot = snapshot_filesystem(container.id)
        filesystem_diff = diff_filesystem(before_snapshot, after_snapshot)

        stdout = _read_container_file(container.id, stdout_path)
        stderr = _read_container_file(container.id, stderr_path)
        strace_log = _read_container_file(container.id, trace_path)
    except DockerException as exc:
        runtime_error = f"Docker execution failed: {exc}"
        status = "error"
    finally:
        if container is not None:
            try:
                container.remove(force=True)
            except DockerException:
                pass

    if runtime_error:
        stderr = f"{stderr}\n{runtime_error}".strip()
    telemetry = parse_strace_trace(strace_log)
    network_hits = _build_network_hits(telemetry)

    if status == "completed" and exit_code is None:
        status = "error"
    elif status == "completed" and exit_code not in (0, None):
        status = "error"

    result = SandboxResult(
        status=status,
        stdout=stdout,
        stderr=stderr,
        strace_log=strace_log,
        fs_diff=filesystem_diff,
        network_hits=network_hits,
        exit_code=exit_code,
        timed_out=timed_out,
        telemetry=telemetry,
        filesystem_diff=filesystem_diff,
    )
    return result.to_dict()
