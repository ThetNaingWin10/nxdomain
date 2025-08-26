#!/usr/bin/env bash
set -euo pipefail

# ---- Configuration ---------------------------------------------------------
PY=python3
COV=coverage
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCHER="$ROOT_DIR/launcher.py"
SERVER="$ROOT_DIR/server.py"
RECURSOR="$ROOT_DIR/recursor.py"
VERIFIER="$ROOT_DIR/verifier.py"
TESTS_DIR="$ROOT_DIR/tests"

# zsh-safe printer for lines containing '!'
p() { printf '%s\n' "$*"; }

# Fresh coverage DB
$COV erase

TMPDIR="$(mktemp -d)"
cleanup() {
  # best-effort shutdown for any ports we started
  for port in ${PORTS:-}; do
    p '!EXIT' | nc -w 1 127.0.0.1 "$port" >/dev/null 2>&1 || true
  done
  rm -rf "$TMPDIR"
}
trap cleanup EXIT
PORTS=""

# Utility: start a server under coverage, record its port
start_server() {
  local conf="$1"
  local port
  port="$(head -n1 "$conf" | tr -d '\r')"
  if [[ ! "$port" =~ ^[0-9]+$ ]]; then
    echo "Bad header in $conf: '$port'" >&2; exit 1
  fi
  echo "Starting server $(basename "$conf") on $port"
  $COV run --append "$SERVER" "$conf" >/dev/null 2>&1 &
  sleep 0.2
  PORTS+=" $port"
}

# ----------------------------------------------------------------------------
# 1) server.py argument errors & invalid file paths
# ----------------------------------------------------------------------------
$COV run --append "$SERVER" || true                       # no args
$COV run --append "$SERVER" a b || true                   # too many args
$COV run --append "$SERVER" "$TMPDIR/does_not_exist" || true

# ----------------------------------------------------------------------------
# 2) server.py invalid configuration files
# ----------------------------------------------------------------------------
BAD1="$TMPDIR/bad_header.conf"          # non-numeric header
printf 'notaport\ncom,1025\n' > "$BAD1"
$COV run --append "$SERVER" "$BAD1" || true

BAD2="$TMPDIR/bad_line.conf"            # missing comma
printf '1024\ncom 1025\n' > "$BAD2"
$COV run --append "$SERVER" "$BAD2" || true

BAD3="$TMPDIR/bad_host.conf"            # illegal hostname '@'
printf '1024\ninv@lid,1025\n' > "$BAD3"
$COV run --append "$SERVER" "$BAD3" || true

BAD4="$TMPDIR/bad_port.conf"            # non-numeric port
printf '1024\ncom,abc\n' > "$BAD4"
$COV run --append "$SERVER" "$BAD4" || true

BAD5="$TMPDIR/bad_range.conf"           # out-of-range port
printf '1024\ncom,70000\n' > "$BAD5"
$COV run --append "$SERVER" "$BAD5" || true

# ----------------------------------------------------------------------------
# 3) launcher.py -> generate singles from a master
# ----------------------------------------------------------------------------
MASTER="$TMPDIR/master.conf"
cat > "$MASTER" <<'EOF'
55000
www.example.com,12345
EOF
SINGLES="$TMPDIR/out"; mkdir -p "$SINGLES"
$COV run --append "$LAUNCHER" "$MASTER" "$SINGLES"

# ----------------------------------------------------------------------------
# 4) verifier.py paths
# ----------------------------------------------------------------------------
# eq
OUT1="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"
[[ "$OUT1" == eq ]]
# invalid arguments (special-cased testing.conf name)
TOX="$TMPDIR/testing.conf"; cp "$MASTER" "$TOX"
OUTX="$($COV run --append "$VERIFIER" "$TOX" "$SINGLES")"
[[ "$OUTX" == "invalid arguments" ]]
# invalid master (non-numeric header)
BADM="$TMPDIR/bad_master.conf"; printf 'notaport\nwww.x.com,1\n' > "$BADM"
OUTM="$($COV run --append "$VERIFIER" "$BADM" "$SINGLES" || true)"; [[ "$OUTM" == "invalid master" ]]
# invalid single (space inside non-header line)
cp "$SINGLES/root.conf" "$SINGLES/root.conf.bak"
awk 'NR==2{print "com, 55001"; next} {print}' "$SINGLES/root.conf" > "$SINGLES/root.conf.tmp" && mv "$SINGLES/root.conf.tmp" "$SINGLES/root.conf"
OUTS="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES" || true)"; [[ "$OUTS" == "invalid single" ]]
mv "$SINGLES/root.conf.bak" "$SINGLES/root.conf"
# neq (break an auth mapping)
AUTH="$SINGLES/auth-example.com.conf"; cp "$AUTH" "$AUTH.bak"
awk 'NR==1{print; next} /^www\.example\.com,/{print "www.example.com,9999"; next} {print}' "$AUTH" > "$AUTH.tmp" && mv "$AUTH.tmp" "$AUTH"
OUTN="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUTN" == neq ]]
mv "$AUTH.bak" "$AUTH"
# back to eq
OUT2="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUT2" == eq ]]

# neq: tld file exists but missing required SLD mapping
cp "$SINGLES/tld-com.conf" "$SINGLES/tld-com.conf.bak"
grep -v '^example\.com,' "$SINGLES/tld-com.conf" > "$SINGLES/tld-com.conf.tmp" || true
mv "$SINGLES/tld-com.conf.tmp" "$SINGLES/tld-com.conf"
OUTTLD="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUTTLD" == neq ]]
mv "$SINGLES/tld-com.conf.bak" "$SINGLES/tld-com.conf"

# eq: extra unrelated TLD in root and tld-foo.conf should be ignored
printf 'foo,56000\n' >> "$SINGLES/root.conf"
cat > "$SINGLES/tld-foo.conf" <<'EOF'
56000
bar,56001
EOF
OUTEQEXTRA="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUTEQEXTRA" == eq ]]
# restore root.conf without extra line
sed -i '' '$ d' "$SINGLES/root.conf" 2>/dev/null || sed -i '$ d' "$SINGLES/root.conf"
rm -f "$SINGLES/tld-foo.conf"

# ----------------------------------------------------------------------------
# 5) Start real servers and exercise admin commands + resolve path
# ----------------------------------------------------------------------------
start_server "$SINGLES/root.conf"
start_server "$SINGLES/tld-com.conf"
start_server "$SINGLES/auth-example.com.conf"

# Early: cover server empty-read branch while server is running
( exec 3<>/dev/tcp/127.0.0.1/55002; exec 3>&- ) || true
sleep 0.1

# Admin commands (OK / INVALID)
p '!ADD www.added.com 55555' | nc -w 1 127.0.0.1 55002 >/dev/null
p '!DEL www.added.com'       | nc -w 1 127.0.0.1 55002 >/dev/null
p '!ADD bad@host 1234'       | nc -w 1 127.0.0.1 55002 >/dev/null
p '!DEL bad@host'            | nc -w 1 127.0.0.1 55002 >/dev/null

p '!ADD www.bad.com 70000'  | nc -w 1 127.0.0.1 55002 >/dev/null   # out-of-range port
p '!ADD www.bad.com notnum' | nc -w 1 127.0.0.1 55002 >/dev/null   # non-numeric port
p '!DEL -bad.com'           | nc -w 1 127.0.0.1 55002 >/dev/null   # invalid hostname

# Resolver success
OUTR1="$($COV run --append "$RECURSOR" www.example.com 127.0.0.1 55000 5)"
[[ "$OUTR1" == "www.example.com,12345" ]]

# Resolver: uppercase and trailing dot normalization
OUTR1B="$($COV run --append "$RECURSOR" WWW.EXAMPLE.COM. 127.0.0.1 55000 5)"
[[ "$OUTR1B" == "www.example.com,12345" ]]

# Resolver INVALID input
OUTR2="$($COV run --append "$RECURSOR" google.com 127.0.0.1 55000 5)" || true
[[ "$OUTR2" == "INVALID" ]]

# Resolver NXDOMAIN (unknown host)
OUTR3="$($COV run --append "$RECURSOR" nope.example.com 127.0.0.1 55000 5)" || true
[[ "$OUTR3" == "NXDOMAIN" ]]

# Resolver connection error (ask a non-running port)
OUTR4="$($COV run --append "$RECURSOR" www.example.com 127.0.0.1 55999 1)" || true
[[ "$OUTR4" == "NXDOMAIN" ]]

# Resolver total-timeout path: connect to tld but not to auth
# Stop auth server only
p '!EXIT' | nc -w 1 127.0.0.1 55002 >/dev/null 2>&1 || true
sleep 0.2
OUTR5="$($COV run --append "$RECURSOR" www.example.com 127.0.0.1 55000 1)" || true
[[ "$OUTR5" == "NXDOMAIN" ]]

# Bring auth back for clean shutdown
start_server "$SINGLES/auth-example.com.conf"

# Clean shutdown of servers
for port in $PORTS; do
  p '!EXIT' | nc -w 1 127.0.0.1 "$port" >/dev/null 2>&1 || true
  sleep 0.05
done

# ----------------------------------------------------------------------------
# 5b) Additional recursor CLI/arg error coverage
# ----------------------------------------------------------------------------
$COV run --append "$RECURSOR" || true                         # no args
$COV run --append "$RECURSOR" www.example.com 127.0.0.1 1024 || true  # missing timeout
$COV run --append "$RECURSOR" www.example.com badip 1024 1   || true  # bad IP string still flows into socket error
$COV run --append "$RECURSOR" www.example.com 127.0.0.1 notaport 1 || true
$COV run --append "$RECURSOR" www.example.com 127.0.0.1 1024 notime || true

# ----------------------------------------------------------------------------
# 4b) Additional verifier branches
# ----------------------------------------------------------------------------
# singles io error: non-existent directory
OUTV1="$($COV run --append "$VERIFIER" "$MASTER" "$TMPDIR/does_not_exist_dir" || true)"; [[ "$OUTV1" == "singles io error" ]]
# singles io error: path exists but is a file
fakefile="$TMPDIR/not_a_dir"; echo x > "$fakefile"
OUTV2="$($COV run --append "$VERIFIER" "$MASTER" "$fakefile" || true)"; [[ "$OUTV2" == "singles io error" ]]

# neq: missing root.conf
mv "$SINGLES/root.conf" "$SINGLES/root.conf.bak"
OUTV3="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUTV3" == "neq" ]]
mv "$SINGLES/root.conf.bak" "$SINGLES/root.conf"

# neq: root header port mismatch
cp "$SINGLES/root.conf" "$SINGLES/root.conf.bak"
awk 'NR==1{print 55999; next} {print}' "$SINGLES/root.conf" > "$SINGLES/root.tmp" && mv "$SINGLES/root.tmp" "$SINGLES/root.conf"
OUTV4="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUTV4" == "neq" ]]
mv "$SINGLES/root.conf.bak" "$SINGLES/root.conf"

# neq: TLD referenced by master but missing corresponding tld-<tld>.conf
mv "$SINGLES/tld-com.conf" "$SINGLES/tld-com.conf.bak"
OUTV5="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUTV5" == "neq" ]]
mv "$SINGLES/tld-com.conf.bak" "$SINGLES/tld-com.conf"

# neq: missing required auth-<sld>.conf
mv "$SINGLES/auth-example.com.conf" "$SINGLES/auth-example.com.conf.bak"
OUTV6="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUTV6" == "neq" ]]
mv "$SINGLES/auth-example.com.conf.bak" "$SINGLES/auth-example.com.conf"

# neq: auth header mismatch vs tld-advertised port
cp "$SINGLES/auth-example.com.conf" "$SINGLES/auth-example.com.conf.bak"
awk 'NR==1{print 55998; next} {print}' "$SINGLES/auth-example.com.conf" > "$SINGLES/auth-example.com.tmp" && mv "$SINGLES/auth-example.com.tmp" "$SINGLES/auth-example.com.conf"
OUTV7="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUTV7" == "neq" ]]
mv "$SINGLES/auth-example.com.conf.bak" "$SINGLES/auth-example.com.conf"

# ----------------------------------------------------------------------------
# 3b) Additional launcher branches (argcount and bad paths)
# ----------------------------------------------------------------------------
$COV run --append "$LAUNCHER" || true                    # no args
$COV run --append "$LAUNCHER" "$MASTER" || true         # one arg only
$COV run --append "$LAUNCHER" "$TMPDIR/does_not_exist_master" "$SINGLES" || true
# outdir exists but is a file
ODFILE="$TMPDIR/outfile"; echo x > "$ODFILE"
$COV run --append "$LAUNCHER" "$MASTER" "$ODFILE" || true

# ----------------------------------------------------------------------------
# 3c) Launcher: more edge cases to lift uncovered lines
# ----------------------------------------------------------------------------
# Empty master file -> INVALID MASTER or NON-WRITABLE SINGLE DIR
EMPTY_MASTER="$TMPDIR/empty_master.conf"; : > "$EMPTY_MASTER"
$COV run --append "$LAUNCHER" "$EMPTY_MASTER" "$SINGLES" || true

# Master header is numeric but outdir not writable
LOCKED_DIR="$TMPDIR/locked_out"; mkdir -p "$LOCKED_DIR"; chmod 000 "$LOCKED_DIR" || true
$COV run --append "$LAUNCHER" "$MASTER" "$LOCKED_DIR" || true
chmod 755 "$LOCKED_DIR" || true

# Master with invalid FQDN forms to hit label validations
BADM2="$TMPDIR/bad_master2.conf"
cat > "$BADM2" <<'EOF'
55000
-evil.com,1
EOF
$COV run --append "$LAUNCHER" "$BADM2" "$SINGLES" || true

BADM3="$TMPDIR/bad_master3.conf"
cat > "$BADM3" <<'EOF'
55000
bad_.example.com,1
EOF
$COV run --append "$LAUNCHER" "$BADM3" "$SINGLES" || true

BADM4="$TMPDIR/bad_master4.conf"
cat > "$BADM4" <<'EOF'
55000
ab"cd.example.com,1
EOF
$COV run --append "$LAUNCHER" "$BADM4" "$SINGLES" || true

# ----------------------------------------------------------------------------
# 5c) Recursor: force non-numeric and empty replies from servers
# ----------------------------------------------------------------------------
# Start a tiny mock root that replies with non-numeric TLD port (to cover ValueError path)
MOCK_PORT=55990
$PY - <<'PY' &
import socket
HOST, PORT = '127.0.0.1', 55990
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT)); s.listen(1)
while True:
    c,_ = s.accept()
    with c:
        c.recv(1024)
        c.sendall(b'notanumber\n')
PY
MOCK_PID=$!
sleep 0.2
OUTR6="$($COV run --append "$RECURSOR" www.example.com 127.0.0.1 $MOCK_PORT 2)" || true
[[ "$OUTR6" == "NXDOMAIN" ]]
kill $MOCK_PID >/dev/null 2>&1 || true

# Start a mock root that returns numeric, then mock TLD that returns NXDOMAIN
ROOTP=55991; TLDP=55992
$PY - <<'PY' &
import socket
HOST='127.0.0.1'
# root
sr=socket.socket(); sr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
sr.bind((HOST,55991)); sr.listen(1)
while True:
    c,_=sr.accept()
    with c:
        c.recv(1024)
        c.sendall(b'55992\n')
PY
RPID=$!
$PY - <<'PY' &
import socket
HOST='127.0.0.1'
st=socket.socket(); st.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
st.bind((HOST,55992)); st.listen(1)
while True:
    c,_=st.accept()
    with c:
        c.recv(1024)
        c.sendall(b'NXDOMAIN\n')
PY
TPID=$!
sleep 0.2
OUTR7="$($COV run --append "$RECURSOR" www.example.com 127.0.0.1 $ROOTP 2)" || true
[[ "$OUTR7" == "NXDOMAIN" ]]
kill $RPID $TPID >/dev/null 2>&1 || true

# Start a mock chain where auth sends empty payload to hit empty-recv/None path
ROOTP=55993; TLDP=55994; AUTHP=55995
$PY - <<'PY' &
import socket
HOST='127.0.0.1'
# root -> tld port
sr=socket.socket(); sr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
sr.bind((HOST,55993)); sr.listen(1)
while True:
    c,_=sr.accept()
    with c:
        c.recv(1024)
        c.sendall(b'55994\n')
PY
R2=$!
$PY - <<'PY' &
import socket
HOST='127.0.0.1'
# tld -> auth port
st=socket.socket(); st.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
st.bind((HOST,55994)); st.listen(1)
while True:
    c,_=st.accept()
    with c:
        c.recv(1024)
        c.sendall(b'55995\n')
PY
T2=$!
$PY - <<'PY' &
import socket
HOST='127.0.0.1'
# auth -> send nothing then close
sa=socket.socket(); sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
sa.bind((HOST,55995)); sa.listen(1)
while True:
    c,_=sa.accept()
    with c:
        c.recv(1024)
        # send nothing (empty)
PY
A2=$!
sleep 0.2
OUTR8="$($COV run --append "$RECURSOR" www.example.com 127.0.0.1 $ROOTP 2)" || true
[[ "$OUTR8" == "NXDOMAIN" ]]
kill $R2 $T2 $A2 >/dev/null 2>&1 || true

# ----------------------------------------------------------------------------
# 4c) verifier: cover extra, unrelated files in singles dir
# ----------------------------------------------------------------------------
EXTRA_FILE="$SINGLES/extra-ignore.conf"; printf '9999\nfoo,1\n' > "$EXTRA_FILE"
OUT2b="$($COV run --append "$VERIFIER" "$MASTER" "$SINGLES")"; [[ "$OUT2b" == eq ]]


# ----------------------------------------------------------------------------
# EXTRA: Broader launcher/verifier/recursor/server coverage to push toward 100%
# ----------------------------------------------------------------------------
# Create a richer master with multiple TLDs and mixed casing/whitespace
MASTER2="$TMPDIR/master2.conf"
cat > "$MASTER2" <<'EOF'
56000
  WWW.Example.COM  , 12345  
www.usyd.edu.au,4242

EOF
SINGLES2="$TMPDIR/out2"; mkdir -p "$SINGLES2"
$COV run --append "$LAUNCHER" "$MASTER2" "$SINGLES2" || true

# Verifier should accept normalized data
OUT_M2_EQ="$($COV run --append "$VERIFIER" "$MASTER2" "$SINGLES2" || true)"; [[ "$OUT_M2_EQ" == eq ]]

# Start servers for the AU chain and resolve via recursor
start_server "$SINGLES2/root.conf"
if [[ -f "$SINGLES2/tld-au.conf" ]]; then start_server "$SINGLES2/tld-au.conf"; fi
if [[ -f "$SINGLES2/auth-edu.au.conf" ]]; then start_server "$SINGLES2/auth-edu.au.conf"; fi
OUT_USYD="$($COV run --append "$RECURSOR" www.usyd.edu.au 127.0.0.1 56000 5)" || true
# Depending on launcher, final leaf may be the port only or fqdn,port; accept either
[[ "$OUT_USYD" == "www.usyd.edu.au,4242" || "$OUT_USYD" == "4242" ]]

# Server admin: unknown command and wrong arity
p '!NOPE something'        | nc -w 1 127.0.0.1 55002 >/dev/null || true
p '!ADD onlyone'           | nc -w 1 127.0.0.1 55002 >/dev/null || true
p '!DEL'                   | nc -w 1 127.0.0.1 55002 >/dev/null || true

# Recursor INVALIDs: underscore label and leading/trailing hyphen
OUT_INV1="$($COV run --append "$RECURSOR" bad_.example.com 127.0.0.1 55000 5)" || true
[[ "$OUT_INV1" == "INVALID" ]]
OUT_INV2="$($COV run --append "$RECURSOR" -bad.example.com 127.0.0.1 55000 5)" || true
[[ "$OUT_INV2" == "INVALID" ]]
OUT_INV3="$($COV run --append "$RECURSOR" bad-.example.com 127.0.0.1 55000 5)" || true
[[ "$OUT_INV3" == "INVALID" ]]

# Mock TLD returning non-numeric auth port to hit ValueError path in auth step
ROOTP=55996; TLDP=55997
$PY - <<'PY' &
import socket
HOST='127.0.0.1'
sr=socket.socket(); sr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
sr.bind((HOST,55996)); sr.listen(1)
while True:
    c,_=sr.accept()
    with c:
        c.recv(1024)
        c.sendall(b'55997\n')
PY
RPID2=$!
$PY - <<'PY' &
import socket
HOST='127.0.0.1'
st=socket.socket(); st.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
st.bind((HOST,55997)); st.listen(1)
while True:
    c,_=st.accept()
    with c:
        c.recv(1024)
        c.sendall(b'NaN\n')
PY
TPID2=$!
sleep 0.2
OUT_BAD_AUTH="$($COV run --append "$RECURSOR" www.example.com 127.0.0.1 $ROOTP 2)" || true
[[ "$OUT_BAD_AUTH" == "NXDOMAIN" ]]
kill $RPID2 $TPID2 >/dev/null 2>&1 || true

# Clean up second chain
for port in $PORTS; do
  p '!EXIT' | nc -w 1 127.0.0.1 "$port" >/dev/null 2>&1 || true
  sleep 0.02
done
PORTS=""

# ----------------------------------------------------------------------------
# 6) Final coverage report
# ----------------------------------------------------------------------------
$COV report -m
