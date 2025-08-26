#!/usr/bin/env bash
set -euo pipefail

# Simple helper to generate single-file configs, start servers, run the recursor
# against the example domain and then shut the servers down.

HERE="$(cd "$(dirname "$0")/.." && pwd)"
TMPDIR=$(mktemp -d)

echo "Using temporary directory: $TMPDIR"
cp "$HERE/examples/master_example.conf" "$TMPDIR/master.conf"

# Generate single-file configs into TMPDIR
python3 "$HERE/launcher.py" "$TMPDIR/master.conf" "$TMPDIR"

pids=()
ports=()

# Start a server for each generated .conf file
for f in "$TMPDIR"/*.conf; do
  base="$(basename "$f")"
  # Skip the master file; only per-server configs have a header port
  if [[ "$base" == "master.conf" ]]; then
    continue
  fi
  port_line="$(head -n1 "$f" | tr -d '\r')"
  # Require a numeric TCP port
  if [[ ! "$port_line" =~ ^[0-9]+$ ]]; then
    echo "Skipping $f (invalid header: '$port_line')" >&2
    continue
  fi
  port="${port_line}"
  if (( port < 1 || port > 65535 )); then
    echo "Skipping $f (out-of-range port: $port)" >&2
    continue
  fi
  echo "Starting server for $f on port $port"
  python3 "$HERE/server.py" "$f" &
  pids+=("$!")
  ports+=("$port")
done

# Give servers a moment to start
sleep 0.5

root_port=$(head -n1 "$TMPDIR/root.conf" | tr -d '\r')

echo "Running recursor for www.example.com against 127.0.0.1:$root_port"
python3 "$HERE/recursor.py" "www.example.com" 127.0.0.1 "$root_port" 5 || true

# Send !EXIT to each server to shut them down cleanly
for p in "${ports[@]}"; do
  printf "!EXIT\n" | nc 127.0.0.1 "$p" || true
done

# Wait for background processes to exit
for pid in "${pids[@]}"; do
  wait "$pid" || true
done

rm -rf "$TMPDIR"

echo "Example run complete."
