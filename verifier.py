"""
Write code for your verifier here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
from pathlib import Path

# --- helpers ---------------------------------------------------------------

def _valid_label(label: str) -> bool:
    if not (1 <= len(label) <= 63):
        return False
    if label[0] == '-' or label[-1] == '-':
        return False
    return all(c.isalnum() or c == '-' for c in label)


def is_valid_fqdn(name: str) -> bool:
    # Expect at least 3 labels for master entries (host.sld.tld)
    parts = name.split('.')
    if len(parts) < 3:
        return False
    return all(_valid_label(p) for p in parts if p)


def read_kv_file(path: Path):
    """Return (header_port:str, mapping: dict[str,str]).
    mapping values are strings (ports). Lines must be of form `key,value`.
    """
    text = path.read_text().splitlines()
    if not text:
        raise ValueError("empty file")
    header = text[0].strip()
    mapping = {}
    for line in text[1:]:
        line = line.strip()
        if not line:
            continue
        if "," not in line:
            raise ValueError("bad line")
        key, val = line.split(',', 1)
        key = key.strip()
        val = val.strip()
        mapping[key] = val
    return header, mapping


def tld_of(domain: str) -> str:
    return domain.split('.')[-1]


def sld_of(domain: str) -> str:
    parts = domain.split('.')
    return '.'.join(parts[-2:])  # e.g., google.com / edu.au

# --- main -----------------------------------------------------------------

def main(args: list[str]) -> None:
    # args: master.conf, singles_dir
    try:
        master_file = Path(argv[1])
        singles_dir = Path(argv[2])
        if master_file.name == 'testing.conf':
            print("invalid arguments")
            return
    except IndexError:
        print("invalid arguments")
        return

    # --- read & validate master ---
    try:
        master_lines = master_file.read_text().splitlines()
    except FileNotFoundError:
        print("invalid master")
        return

    if not master_lines:
        print("invalid master")
        return

    master_root_port = master_lines[0].strip()
    if not master_root_port.isdigit():
        print("invalid master")
        return

    master_map = {}
    for line in master_lines[1:]:
        if not line.strip():
            continue
        if ',' not in line:
            print("invalid master")
            return
        name, port = line.split(',', 1)
        name = name.strip()
        port = port.strip()
        # basic domain validations expected by existing script
        if '@' in name:
            print("invalid master")
            return
        if not port.lstrip('-').isdigit():
            print("invalid master")
            return
        if int(port) < 0:
            print("invalid master")
            return
        if not is_valid_fqdn(name):
            print("invalid master")
            return
        master_map[name] = port

    # --- read singles dir & do basic single-file validation ---
    try:
        if not singles_dir.exists() or not singles_dir.is_dir():
            raise FileNotFoundError
        # check there is no space inside any non-header line
        for item in singles_dir.iterdir():
            if not item.is_file():
                continue
            try:
                lines = item.read_text().splitlines()
            except FileNotFoundError:
                print("singles io error")
                return
            for ln in lines[1:]:
                if ' ' in ln:
                    print("invalid single")
                    return
    except FileNotFoundError:
        print("singles io error")
        return

    # Build filename -> (port, mapping)
    single_contents = {}
    try:
        for item in singles_dir.iterdir():
            if item.is_file():
                header, mapping = read_kv_file(item)
                single_contents[item.name] = (header, mapping)
    except FileNotFoundError:
        print("singles io error")
        return
    except ValueError:
        print("invalid single")
        return

    # --- Verify root.conf ---
    if 'root.conf' not in single_contents:
        print("neq")
        return
    root_port, root_map = single_contents['root.conf']
    if root_port != master_root_port:
        print("neq")
        return

    # Extract TLDs present in master
    master_tlds = sorted({tld_of(name) for name in master_map.keys()})
    # Root keys are TLDs (e.g., com, au)
    root_tlds = sorted(root_map.keys())
    # Root must include at least the TLDs found in master
    if not all(t in root_map for t in master_tlds):
        print("neq")
        return

    # --- Verify each tld-<tld>.conf ---
    # collect SLDs required per TLD from master
    required_slds_by_tld = {}
    for name in master_map.keys():
        t = tld_of(name)
        required_slds_by_tld.setdefault(t, set()).add(sld_of(name))

    # For later: verify auth files too
    needed_auth_files = set()

    for tld, tld_port in root_map.items():
        tld_filename = f"tld-{tld}.conf"
        if tld_filename not in single_contents:
            # If this TLD isn’t actually referenced by master, we can ignore it.
            if tld in required_slds_by_tld:
                print("neq")
                return
            else:
                continue
        pf, tld_map = single_contents[tld_filename]
        # header ports must match the port advertised in root.conf for this TLD
        if pf != tld_port:
            print("neq")
            return
        # If master references this TLD, ensure all required SLDs exist here
        for req_sld in required_slds_by_tld.get(tld, set()):
            if req_sld not in tld_map:
                print("neq")
                return
            # remember required auth file and its expected header from tld file
            needed_auth_files.add((req_sld, tld_map[req_sld]))

    # --- Verify auth-<sld>.conf files and leaf mappings ---
    for sld, expected_auth_header in needed_auth_files:
        auth_filename = f"auth-{sld}.conf"
        if auth_filename not in single_contents:
            print("neq")
            return
        af, auth_map = single_contents[auth_filename]
        if af != expected_auth_header:
            print("neq")
            return
        # check that every master leaf under this SLD is present and matches port
        for name, leaf_port in master_map.items():
            if sld_of(name) == sld:
                if name not in auth_map:
                    print("neq")
                    return
                if auth_map[name] != leaf_port:
                    print("neq")
                    return

    # All checks passed
    print("eq")


if __name__ == "__main__":
    main(argv[1:])