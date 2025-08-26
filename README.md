# NXDOMAIN — simplified DNS (INFO1112)

A small, educational DNS-like system in Python. It includes:
- a launcher that converts a `master.conf` into single-file configs,
- simple TCP DNS servers (root / TLD / authority),
- a recursive resolver that follows root → TLD → auth,
- a verifier that checks the single-file configs against the master.

> Coursework for **INFO1112 (University of Sydney)** — intended for learning and testing only.

---

## Quick Start (macOS/Linux)

Requirements: `python3`, `nc` (netcat).

```bash
# 1) Generate single-file configs
python3 launcher.py /tmp/master.conf /tmp/nxdomain-out

# 2) Start servers in three terminals
python3 server.py /tmp/nxdomain-out/root.conf
python3 server.py /tmp/nxdomain-out/tld-com.conf
python3 server.py /tmp/nxdomain-out/auth-google.com.conf

# 3) Resolve a domain via the recursor
python3 recursor.py www.google.com 127.0.0.1 1024 5
# -> www.google.com,8987

# 4) Verify configs
python3 verifier.py /tmp/master.conf /tmp/nxdomain-out
# -> eq
```

Or run the end-to-end example:

```bash
chmod +x scripts/run_example.sh
./scripts/run_example.sh
```

---

## Components

- `launcher.py` — generates:
  - `root.conf` (TLD → port),
  - `tld-<tld>.conf` (SLD → auth port),
  - `auth-<sld>.conf` (FQDN → final port).
- `server.py` — serves records from a single config; binds `127.0.0.1:<header-port>`.
- `recursor.py` — 3-hop resolver (root → TLD → auth) with a total timeout; prints `fqdn,port` or `NXDOMAIN`.
- `verifier.py` — checks that singles are consistent with `master.conf`.

---

## Configuration formats

**`master.conf`**
- Line 1: root server port (recommend **1024–65535**).
- Following lines: `fqdn,port` where:
  - FQDN has ≥ 3 labels (host.sld.tld),
  - labels are 1–63 chars, alnum or `-`, not starting/ending with `-`,
  - port is decimal in **1024–65535**.

**Singles (from `launcher.py`)**
- `root.conf`: first line root port; then `tld,port`.
- `tld-<tld>.conf`: first line TLD port; then `sld,port` (e.g., `google.com,55002`).
- `auth-<sld>.conf`: first line auth port; then `fqdn,port` (e.g., `www.google.com,8987`).

Files are newline-separated text; blank lines are ignored.

---

## Admin commands (server)

Send a newline-terminated command to `127.0.0.1:<port>`:

- `!ADD <hostname> <port>` → `OK` / `INVALID`
- `!DEL <hostname>` → `OK` / `INVALID`
- `!EXIT` → `OK` and the server exits

**Example (zsh-safe):**
```bash
printf '%s\n' '!ADD www.example.com 12345' | nc 127.0.0.1 <port>
```

---

## Troubleshooting

- `INVALID CONFIGURATION` / `invalid master/single`: check for non-numeric header ports, invalid hostnames, spaces in mapping lines, or missing `key,value`.
- `NXDOMAIN` in recursor: ensure root/TLD/auth servers are running on the ports advertised in their configs.
- zsh eats `!`: use `printf '%s\n' '!...'` or `set +H`.

---

## License

Educational use only. Keep the repository private if required by coursework policy.
