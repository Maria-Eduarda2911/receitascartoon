#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ -d "$ROOT_DIR/.venv" ]; then
  source "$ROOT_DIR/.venv/bin/activate"
fi

export USE_SQLITE=1

stop_previous_app() {
  for port in 5000 5005; do
    if command -v lsof >/dev/null 2>&1; then
      pids="$(lsof -ti "tcp:${port}" 2>/dev/null || true)"
      if [ -n "$pids" ]; then
        echo "Parando processos da porta ${port}: ${pids}"
        kill $pids 2>/dev/null || true
        sleep 1
        kill -9 $pids 2>/dev/null || true
      fi
    elif command -v fuser >/dev/null 2>&1; then
      fuser -k "${port}/tcp" >/dev/null 2>&1 || true
    fi
  done

  pkill -f "flask --app app run" >/dev/null 2>&1 || true
  pkill -f "python.*app.py" >/dev/null 2>&1 || true
  pkill -f "gunicorn.*app" >/dev/null 2>&1 || true
}

stop_previous_app

PORT=5000
for candidate in 5000 5005; do
  if python3 - "$candidate" <<'PY'
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind(('127.0.0.1', port))
    raise SystemExit(0)
except OSError:
    raise SystemExit(1)
finally:
    s.close()
PY
  then
    PORT="$candidate"
    break
  fi
done

cd "$ROOT_DIR/app"

echo ""
echo "====================================================="
echo "Receitas Toon"
echo "Acesse: http://localhost:${PORT}"
echo "====================================================="
echo ""

echo "Iniciando app em http://localhost:${PORT}"
flask --app app run --host 0.0.0.0 --port "$PORT"
