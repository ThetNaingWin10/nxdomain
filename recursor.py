"""
Write code for your recursor here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
import socket
import sys
import time

ENCODING = "utf-8"


def _valid_label(label: str) -> bool:
    return (
        1 <= len(label) <= 63
        and label[0] != '-' and label[-1] != '-'
        and all(c.isalnum() or c == '-' for c in label)
    )


def is_valid_domain(domain_name: str) -> bool:
    parts = domain_name.split('.')
    if len(parts) < 3:
        return False
    return all(_valid_label(p) for p in parts if p)


def _query_once(name: str, ip: str, port: int, timeout: float) -> str | None:
    """Send single-line query `name` to (ip, port) with timeout seconds.
    Returns decoded response (stripped) or None on timeout/error.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.sendall(f"{name}\n".encode(ENCODING))
            data = sock.recv(1024)
            if not data:
                return None
            return data.decode(ENCODING).strip()
    except (socket.timeout, OSError):
        return None


def resolve_domain(domain: str, root_ip: str, root_port: int, timeout_total: int) -> None:
    """Resolve `domain` by querying root -> tld -> auth within a total deadline.
    Prints the final mapping (e.g., "www.google.com,8987") or "NXDOMAIN".
    """
    start = time.monotonic()

    # 1) Ask ROOT for the TLD (e.g., "com") -> returns TLD server port
    labels = domain.split('.')
    tld = labels[-1]
    remaining = max(0.01, timeout_total - (time.monotonic() - start))
    r = _query_once(tld, root_ip, root_port, remaining)
    if not r or 'NXDOMAIN' in r:
        print('NXDOMAIN')
        return
    try:
        tld_port = int(r)
    except ValueError:
        print('NXDOMAIN')
        return

    # 2) Ask TLD server for the SLD (e.g., "google.com") -> returns auth server port
    sld = '.'.join(labels[-2:])
    remaining = max(0.01, timeout_total - (time.monotonic() - start))
    r = _query_once(sld, root_ip, tld_port, remaining)
    if not r or 'NXDOMAIN' in r:
        print('NXDOMAIN')
        return
    try:
        auth_port = int(r)
    except ValueError:
        print('NXDOMAIN')
        return

    # 3) Ask AUTH server for the full domain (e.g., "www.google.com") -> final mapping
    remaining = max(0.01, timeout_total - (time.monotonic() - start))
    r = _query_once(domain, root_ip, auth_port, remaining)
    if not r or 'NXDOMAIN' in r:
        print('NXDOMAIN')
        return

    print(f"{domain},{r}")


def main() -> None:
    # Usage: recursor.py <domain> <root_ip> <root_port> <timeout_seconds>
    if len(sys.argv) != 5:
        print("usage: recursor.py <domain> <root_ip> <root_port> <timeout>")
        return

    domain_name = sys.argv[1].strip().rstrip('.').lower()
    root_ip = sys.argv[2]
    try:
        root_port = int(sys.argv[3])
        timeout = int(sys.argv[4])
    except ValueError:
        print("invalid port or timeout")
        return

    if not is_valid_domain(domain_name):
        print("INVALID")
        return

    resolve_domain(domain_name, root_ip, root_port, timeout)


if __name__ == "__main__":
    main()