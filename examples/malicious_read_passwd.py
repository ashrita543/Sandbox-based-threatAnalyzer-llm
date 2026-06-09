from pathlib import Path


def main() -> None:
    data = Path("/etc/passwd").read_text(encoding="utf-8", errors="replace")
    print(data.splitlines()[0])


if __name__ == "__main__":
    main()
