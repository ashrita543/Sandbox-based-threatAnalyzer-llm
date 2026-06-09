import subprocess


def main() -> None:
    # Spawn a child process to trigger process syscalls in strace.
    result = subprocess.run(["sh", "-lc", "echo spawned-child"], capture_output=True, text=True, check=False)
    print(result.stdout.strip())


if __name__ == "__main__":
    main()
