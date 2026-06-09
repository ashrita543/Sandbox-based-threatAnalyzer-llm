import socket


def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect(("1.1.1.1", 443))
    except OSError as exc:
        print(f"connection failed as expected: {exc}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
