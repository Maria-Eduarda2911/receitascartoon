#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ -d "$ROOT_DIR/.venv" ]; then
  source "$ROOT_DIR/.venv/bin/activate"
fi

export USE_SQLITE=1

PORT=5000
if python3 - <<'PY'
import socket
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind(('127.0.0.1', 5000))
    s.close()
    raise SystemExit(0)
except OSError:
    raise SystemExit(1)
PY
then
  PORT=5000
else
  PORT=5005
fi

cd "$ROOT_DIR/app"

echo ""
echo "====================================================="
echo "Receitas Toon"
echo "Acesse: http://localhost:${PORT}"
echo "====================================================="
echo ""

flask --app app run --host 0.0.0.0 --port "$PORT"
