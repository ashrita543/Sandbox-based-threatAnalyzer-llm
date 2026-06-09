from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

FILE_CHANGE_SYSCALLS = {
    "creat",
    "fchmod",
    "fchmodat",
    "fchown",
    "fchownat",
    "link",
    "linkat",
    "mkdir",
    "mkdirat",
    "mknod",
    "mknodat",
    "open",
    "openat",
    "openat2",
    "rename",
    "renameat",
    "renameat2",
    "rmdir",
    "symlink",
    "symlinkat",
    "truncate",
    "unlink",
    "unlinkat",
    "utimensat",
}

PROCESS_SYSCALLS = {
    "clone",
    "clone3",
    "execve",
    "execveat",
    "fork",
    "vfork",
    "wait4",
    "waitid",
}

NETWORK_SYSCALLS = {
    "accept",
    "accept4",
    "bind",
    "connect",
    "getpeername",
    "getsockname",
    "getsockopt",
    "listen",
    "recvfrom",
    "recvmsg",
    "sendmsg",
    "sendmmsg",
    "sendto",
    "setsockopt",
    "shutdown",
    "socket",
    "socketpair",
}

TRACE_LINE_RE = re.compile(
    r"^(?:\[pid\s+(?P<bracket_pid>\d+)\]\s+|(?P<pid>\d+)\s+)?"
    r"(?P<syscall>[a-zA-Z_][a-zA-Z0-9_]*)\((?P<args>.*)\)\s+=\s+(?P<result>.*)$"
)
QUOTED_PATH_RE = re.compile(r'"((?:\\.|[^"\\])*)"')
WRITE_HINTS = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND")


@dataclass(frozen=True)
class TelemetryEvent:
    syscall: str
    pid: str | None
    arguments: str
    result: str
    paths: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TelemetrySnapshot:
    file_changes: list[TelemetryEvent]
    process_activity: list[TelemetryEvent]
    network_attempts: list[TelemetryEvent]
    raw_trace_lines: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_changes": [event.to_dict() for event in self.file_changes],
            "process_activity": [event.to_dict() for event in self.process_activity],
            "network_attempts": [event.to_dict() for event in self.network_attempts],
            "raw_trace_lines": self.raw_trace_lines,
        }


def _unescape_path(path_text: str) -> str:
    return bytes(path_text, "utf-8").decode("unicode_escape")


def _collect_paths(arguments: str) -> list[str]:
    return [_unescape_path(path) for path in QUOTED_PATH_RE.findall(arguments)]


def _is_write_or_mutation(arguments: str, syscall: str) -> bool:
    if syscall in {"creat", "mkdir", "mkdirat", "mknod", "mknodat", "rename", "renameat", "renameat2", "rmdir", "symlink", "symlinkat", "unlink", "unlinkat", "truncate", "utimensat"}:
        return True
    return any(hint in arguments for hint in WRITE_HINTS)


def parse_strace_trace(trace_text: str) -> dict[str, Any]:
    file_changes: list[TelemetryEvent] = []
    process_activity: list[TelemetryEvent] = []
    network_attempts: list[TelemetryEvent] = []

    for raw_line in trace_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("+++") or line.startswith("---"):
            continue

        match = TRACE_LINE_RE.match(line)
        if not match:
            continue

        pid = match.group("pid") or match.group("bracket_pid")
        syscall = match.group("syscall")
        arguments = match.group("args")
        result = match.group("result")
        paths = _collect_paths(arguments)

        event = TelemetryEvent(
            syscall=syscall,
            pid=pid,
            arguments=arguments,
            result=result,
            paths=paths,
        )

        if syscall in FILE_CHANGE_SYSCALLS and paths and _is_write_or_mutation(arguments, syscall) and not result.startswith("-1"):
            file_changes.append(event)
        elif syscall in PROCESS_SYSCALLS:
            process_activity.append(event)
        elif syscall in NETWORK_SYSCALLS:
            network_attempts.append(event)

    snapshot = TelemetrySnapshot(
        file_changes=file_changes,
        process_activity=process_activity,
        network_attempts=network_attempts,
        raw_trace_lines=len(trace_text.splitlines()),
    )
    return snapshot.to_dict()


# ============================================================================
# Phase 3: Log Processing — Parse, Score, and Format for LLM
# ============================================================================

SUSPICIOUS_FILES = [
    "/etc/passwd", "/etc/shadow", "/etc/cron", "/root/",
    "/.bashrc", "/.ssh/", "/tmp/", "/var/spool/cron",
    "/etc/sudoers", "/var/log/", "/etc/hosts"
]

SUSPICIOUS_PROCESSES = [
    "curl", "wget", "nc", "ncat", "bash", "sh", "chmod", "python",
    "perl", "ruby", "node", "java", "gcc", "telnet", "ssh", "scp"
]

SUSPICIOUS_PORTS = ["4444", "1337", "31337", "6666", "9001", "8080", "5555"]


def parse_strace(strace_log: str) -> dict[str, Any]:
    """Extract files, network attempts, and process spawning from strace log."""
    files_accessed = set()
    network_attempts: list[dict[str, Any]] = []
    processes_spawned = set()

    for line in strace_log.splitlines():
        # File access: openat(AT_FDCWD, "/etc/passwd", ...)
        file_match = re.search(r'openat\(.*?"([^"]+)"', line)
        if file_match:
            path = file_match.group(1)
            # Filter out noise (Python internals, shared libs)
            if not any(path.startswith(p) for p in ["/usr/lib", "/usr/local/lib", "/proc", "/sys", "/dev"]):
                files_accessed.add(path)

        # Network: connect() with an IP address or hostname
        net_match = re.search(r'connect\([^,]+,\s*{sa_family=AF_INET,\s*sin_port=htons\((\d+)\),\s*sin_addr=inet_addr\("([^"]+)"\)', line)
        if net_match:
            network_attempts.append({
                "ip": net_match.group(2),
                "port": net_match.group(1)
            })

        # DNS: sendto with hostname query
        dns_match = re.search(r'sendto\([^,]+,\s*".*?([a-zA-Z0-9.-]+\.[a-z]{2,})', line)
        if dns_match:
            domain = dns_match.group(1)
            # Avoid duplicates
            if not any(d.get("dns_query") == domain for d in network_attempts):
                network_attempts.append({"dns_query": domain})

        # Process spawning: execve("/usr/bin/curl", ...)
        exec_match = re.search(r'execve\("([^"]+)"', line)
        if exec_match:
            processes_spawned.add(exec_match.group(1))

    return {
        "files_accessed": sorted(list(files_accessed)),
        "network_attempts": network_attempts,
        "processes_spawned": sorted(list(processes_spawned))
    }


def score_findings(parsed: dict[str, Any], fs_diff: dict[str, Any], network_hits: list[str]) -> list[str]:
    """Tag each finding with suspicion level and generate readable flags."""
    flags: list[str] = []

    # File access signals
    for f in parsed.get("files_accessed", []):
        if any(s in f for s in SUSPICIOUS_FILES):
            flags.append(f"READ sensitive file: {f}")

    # Filesystem mutations
    for f in fs_diff.get("created", []):
        flags.append(f"CREATED file: {f}")
        if "/tmp/" in f or f.endswith(".sh") or f.endswith(".py"):
            flags.append(f"  ^ high suspicion: executable in temp dir")

    for f in fs_diff.get("deleted", []):
        flags.append(f"DELETED file: {f}")

    # Process spawning
    for proc in parsed.get("processes_spawned", []):
        if any(s in proc for s in SUSPICIOUS_PROCESSES):
            flags.append(f"SPAWNED suspicious process: {proc}")

    # Network activity
    for net in parsed.get("network_attempts", []):
        if "dns_query" in net:
            flags.append(f"DNS query: {net['dns_query']}")
        elif "port" in net and "ip" in net:
            label = "^ known C2 port" if net["port"] in SUSPICIOUS_PORTS else ""
            flags.append(f"TCP connect: {net['ip']}:{net['port']} {label}".strip())

    # HTTP network hits
    for hit in network_hits:
        flags.append(f"HTTP request: {hit}")

    return flags


def format_behavioral_summary(raw_output: dict[str, Any]) -> str:
    """
    Convert raw sandbox output into a compact behavioral fingerprint
    suitable for LLM injection (~600 tokens, ~2400 chars).
    """
    strace_log = raw_output.get("strace_log", "")
    parsed = parse_strace(strace_log)
    
    flags = score_findings(
        parsed,
        raw_output.get("fs_diff", {}),
        raw_output.get("network_hits", [])
    )

    lines: list[str] = []

    # Basic execution info
    lines.append(f"Execution status: {raw_output.get('status', 'unknown')}")

    if raw_output.get("stdout"):
        stdout_excerpt = raw_output['stdout'][:300]
        lines.append(f"Script stdout: {stdout_excerpt}")

    if raw_output.get("stderr"):
        stderr_excerpt = raw_output['stderr'][:200]
        lines.append(f"Script stderr: {stderr_excerpt}")

    # Behavioral signals (main block)
    lines.append("\n--- Behavioral Signals ---")
    if flags:
        for flag in flags:
            lines.append(f"  {flag}")
    else:
        lines.append("  No suspicious signals detected.")

    # Summary lists
    lines.append(f"\nFiles created: {raw_output.get('fs_diff', {}).get('created', [])}")
    lines.append(f"Files deleted: {raw_output.get('fs_diff', {}).get('deleted', [])}")
    lines.append(f"Files accessed: {parsed['files_accessed']}")
    lines.append(f"Processes spawned: {parsed['processes_spawned']}")
    lines.append(f"Network attempts: {parsed['network_attempts']}")

    summary = "\n".join(lines)

    # Hard cap at ~2400 chars (~600 tokens) to leave room for the LLM prompt
    # return summary[:2400]
    return summary