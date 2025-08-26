from sys import argv
from pathlib import Path
from typing import Dict, List, Tuple, Set

# -----------------------------
# Validation helpers (spec-compliant)
# -----------------------------

def validate_port(port: str) -> bool:
    """A valid port is a decimal in [1024, 65535]."""
    if not port or not port.isdigit():
        return False
    n = int(port)
    return 1024 <= n <= 65535


def _valid_dns_label(label: str) -> bool:
    """A DNS label may contain A-Z, a-z, 0-9, '-' and cannot start or end with '-'."""
    if not label:
        return False
    # Only alnum or '-'
    for ch in label:
        if not ("a" <= ch <= "z" or "A" <= ch <= "Z" or "0" <= ch <= "9" or ch == "-"):
            return False
    # Cannot start or end with '-'
    if label[0] == '-' or label[-1] == '-':
        return False
    return True


def validate_domain(domain: str) -> bool:
    """Validate hostname per assignment spec (C.B.A).
    - At least 3 labels split by '.'
    - No empty labels (=> no leading/trailing or consecutive dots)
    - Last two labels (B, A) must be valid DNS labels (alnum and '-')
    - Left part (C) is one or more labels that each obey the same label rule
    """
    if not domain:
        return False
    if '@' in domain:
        return False
    parts = domain.split('.')
    if len(parts) < 3:
        return False
    # No empty labels
    for p in parts:
        if p == "":
            return False
    # A and B rules
    A = parts[-1]
    B = parts[-2]
    if not (_valid_dns_label(A) and _valid_dns_label(B)):
        return False
    # C can contain dots, but each label must be valid
    for lbl in parts[:-2]:
        if not _valid_dns_label(lbl):
            return False
    return True


# -----------------------------
# Allocation helpers
# -----------------------------

def next_free_port(start_from: int, used: Set[int]) -> int:
    """Find the next free port in [1024, 65535], starting from start_from,
    wrapping once if needed. Raises RuntimeError if none found."""
    if start_from < 1024:
        start_from = 1024
    candidate = start_from
    wrapped = False
    while True:
        if candidate > 65535:
            if wrapped:
                break
            candidate = 1024
            wrapped = True
            continue
        if candidate not in used:
            return candidate
        candidate += 1
    raise RuntimeError("No free ports available in [1024,65535]")


# -----------------------------
# Core processing
# -----------------------------

def process_master_file(master_path: Path, output_dir: Path) -> None:
    """Process the master configuration and generate single configuration files
    as per spec: root.conf, tld-<tld>.conf, auth-<sld>.conf.
    """
    try:
        raw_lines = master_path.read_text().splitlines()
    except Exception:
        print("INVALID MASTER")
        return

    # Strip and drop blanks
    lines = [ln.strip() for ln in raw_lines if ln.strip() != ""]
    if not lines:
        print("INVALID MASTER")
        return

    root_port_s = lines[0]
    if not validate_port(root_port_s):
        print("INVALID MASTER")
        return
    root_port = int(root_port_s)

    # Parse records
    leaf_map: Dict[str, int] = {}  # hostname -> leaf port
    used_ports: Set[int] = {root_port}

    for ln in lines[1:]:
        # must be exactly one comma separating domain and port
        if ',' not in ln:
            print("INVALID MASTER")
            return
        domain_part, port_part = ln.split(',', 1)
        domain = domain_part.strip()
        port_s = port_part.strip()
        if not (validate_domain(domain) and validate_port(port_s)):
            print("INVALID MASTER")
            return
        port_v = int(port_s)
        # Track used leaf ports to avoid collisions
        used_ports.add(port_v)
        # Detect duplicates with conflicting ports
        if domain in leaf_map and leaf_map[domain] != port_v:
            print("INVALID MASTER")
            return
        leaf_map[domain] = port_v

    # Build TLD and SLD structures
    tld_to_port: Dict[str, int] = {}
    sld_to_port: Dict[str, int] = {}  # key = "<second>.<tld>"
    tld_to_slds: Dict[str, Set[str]] = {}
    auth_records: Dict[str, List[Tuple[str, int]]] = {}

    # Seed collections
    for host, leaf in leaf_map.items():
        parts = host.split('.')
        tld = parts[-1]
        sld = parts[-2] + '.' + parts[-1]  # e.g., google.com
        tld_to_slds.setdefault(tld, set()).add(sld)
        auth_records.setdefault(sld, []).append((host, leaf))

    # Allocate ports for TLD servers and auth servers (stable, collision-free)
    cursor = root_port + 1
    # TLD ports
    for tld in sorted(tld_to_slds.keys()):
        if tld not in tld_to_port:
            p = next_free_port(cursor, used_ports)
            tld_to_port[tld] = p
            used_ports.add(p)
            cursor = p + 1
    # AUTH ports
    for sld in sorted(auth_records.keys()):
        if sld not in sld_to_port:
            p = next_free_port(cursor, used_ports)
            sld_to_port[sld] = p
            used_ports.add(p)
            cursor = p + 1

    # -----------------------------
    # Write out single configuration files
    # -----------------------------
    try:
        # 1) root.conf
        root_config_path = output_dir / "root.conf"
        with root_config_path.open('w', encoding='utf-8') as f:
            f.write(str(root_port))
            for tld in sorted(tld_to_port.keys()):
                f.write(f"\n{tld},{tld_to_port[tld]}")
            f.write("\n")

        # 2) tld-<tld>.conf files
        for tld in sorted(tld_to_slds.keys()):
            tld_conf = output_dir / f"tld-{tld}.conf"
            with tld_conf.open('w', encoding='utf-8') as f:
                f.write(str(tld_to_port[tld]))
                for sld in sorted(tld_to_slds[tld]):
                    f.write(f"\n{sld},{sld_to_port[sld]}")
                f.write("\n")

        # 3) auth-<sld>.conf files (keep dot in sld to avoid collisions across TLDs)
        for sld in sorted(auth_records.keys()):
            safe_name = sld  # dots are fine in filenames; keeps it unambiguous
            auth_conf = output_dir / f"auth-{safe_name}.conf"
            with auth_conf.open('w', encoding='utf-8') as f:
                f.write(str(sld_to_port[sld]))
                for host, leaf in sorted(auth_records[sld]):
                    f.write(f"\n{host},{leaf}")
                f.write("\n")

    except OSError:
        print("INVALID MASTER or NON-WRITABLE SINGLE DIR")
        return


def main(args: List[str]) -> None:
    if len(args) != 3:
        print("INVALID ARGUMENTS")
        return

    master_path = Path(args[1])
    output_dir = Path(args[2])

    if not master_path.exists() or not master_path.is_file():
        print("INVALID MASTER or NON-WRITABLE SINGLE DIR")
        return
    if not output_dir.exists() or not output_dir.is_dir():
        print("INVALID MASTER or NON-WRITABLE SINGLE DIR")
        return

    process_master_file(master_path, output_dir)


if __name__ == "__main__":
    main(argv)
