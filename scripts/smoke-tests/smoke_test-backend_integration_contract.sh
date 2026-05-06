#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://localhost:5000}"
SOCKET_URL="${SOCKET_URL:-http://backend:5000}"
COMPOSE_CMD="${COMPOSE_CMD:-docker compose}"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
  PYTHON_ARGS=()
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
  PYTHON_ARGS=()
elif command -v py >/dev/null 2>&1; then
  PYTHON_BIN="py"
  PYTHON_ARGS=(-3)
else
  echo "Python is required to validate JSON responses."
  exit 1
fi

LAST_STATUS=""
LAST_BODY=""
SOCKET_LISTENER_PID=""

log() {
  echo
  echo "==> $1"
}

run_python() {
  "$PYTHON_BIN" "${PYTHON_ARGS[@]}" "$@"
}

request() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  local response

  if [[ -n "$body" ]]; then
    response="$(curl -sS -X "$method" \
      -H 'Content-Type: application/json' \
      -d "$body" \
      -w $'\n%{http_code}' \
      "${BACKEND_URL}${path}")"
  else
    response="$(curl -sS -X "$method" \
      -w $'\n%{http_code}' \
      "${BACKEND_URL}${path}")"
  fi

  LAST_STATUS="${response##*$'\n'}"
  LAST_BODY="${response%$'\n'*}"
}

assert_status() {
  local expected="$1"
  if [[ "$LAST_STATUS" != "$expected" ]]; then
    echo "Expected HTTP $expected but got $LAST_STATUS"
    echo "$LAST_BODY"
    exit 1
  fi
}

assert_json() {
  local expression="$1"
  local message="$2"

  printf '%s' "$LAST_BODY" | run_python -c \
    'import json, sys
data = json.load(sys.stdin)
expr = sys.argv[1]
message = sys.argv[2]
if not eval(expr, {"__builtins__": {}}, {"data": data, "len": len, "isinstance": isinstance, "int": int, "float": float, "str": str, "dict": dict, "list": list, "bool": bool, "type": type, "abs": abs}):
    raise SystemExit(message)' \
    "$expression" "$message"
}

json_query() {
  local expression="$1"
  printf '%s' "$LAST_BODY" | run_python -c \
    'import json, sys
data = json.load(sys.stdin)
expr = sys.argv[1]
result = eval(expr, {"__builtins__": {}}, {"data": data, "len": len})
print(result)' \
    "$expression"
}

wait_for_backend() {
  log "Starting backend integration stack"
  $COMPOSE_CMD up -d postgres mosquitto
  $COMPOSE_CMD up -d --force-recreate backend frontend gateway tag

  log "Waiting for backend health endpoint"
  for _ in $(seq 1 60); do
    if curl -sf "${BACKEND_URL}/" >/dev/null; then
      return 0
    fi
    sleep 1
  done

  echo "Backend did not become ready in time."
  exit 1
}

publish_mqtt_json() {
  local topic="$1"
  local payload="$2"
  $COMPOSE_CMD exec -T backend python -c \
    "import json, paho.mqtt.client as mqtt; client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2); client.connect('mosquitto', 1883, 60); client.publish('${topic}', json.dumps(${payload})); client.disconnect()"
}

start_socket_listener() {
  local output_file="$1"
  $COMPOSE_CMD exec -T frontend bun --eval \
    "import { io } from 'socket.io-client';
const socketUrl = process.argv[1];
const socket = io(socketUrl, { path: '/socket.io', transports: ['polling'], reconnection: false, timeout: 5000 });
const timeout = setTimeout(() => {
  console.error('Timed out waiting for battery_update event for tag 1.');
  socket.close();
  process.exit(1);
}, 10000);
socket.on('connect_error', (error) => {
  clearTimeout(timeout);
  console.error(error?.message ?? String(error));
  process.exit(1);
});
socket.on('battery_update', (data) => {
  if (data?.tagId === 1) {
    clearTimeout(timeout);
    console.log(JSON.stringify(data));
    socket.close();
    process.exit(0);
  }
});
" "$SOCKET_URL" >"$output_file" 2>&1 &
  SOCKET_LISTENER_PID=$!
}

wait_for_pid() {
  local pid="$1"
  local log_file="${2:-}"
  if ! wait "$pid"; then
    echo "Background process failed."
    if [[ -n "$log_file" && -f "$log_file" ]]; then
      echo "--- background process output ---"
      cat "$log_file"
      echo "--- end background process output ---"
    fi
    exit 1
  fi
}

main() {
  local before_count after_patch_count after_publish_count
  local socket_log

  wait_for_backend

  log "Checking REST health contract"
  request GET /
  assert_status 200
  assert_json 'data["service"] == "backend" and data["status"] == "ok"' "Unexpected response from GET /"

  request GET "/battery?tagId=1"
  assert_status 200
  assert_json 'isinstance(data["battery"], int)' "Expected integer battery from GET /battery?tagId=1"

  request GET /battery
  assert_status 400

  request GET "/battery?tagId=999999"
  assert_status 404

  log "Checking seeded collections required by the contract"
  request GET /api/products
  assert_status 200
  assert_json 'isinstance(data, list) and len(data) >= 1' "Expected seeded products"

  request GET /api/tags
  assert_status 200
  assert_json 'isinstance(data, list) and len(data) >= 1' "Expected seeded tags"

  request GET /api/tag-payloads
  assert_status 200
  before_count="$(json_query 'len(data)')"

  log "Checking product update triggers payload persistence"
  request PATCH /api/products/1 '{"price":23.4}'
  assert_status 200
  assert_json 'abs(float(data["price"]) - 23.4) < 1e-9' "Product price update did not persist"

  request GET /api/tag-payloads
  assert_status 200
  after_patch_count="$(json_query 'len(data)')"
  if (( after_patch_count <= before_count )); then
    echo "Expected product update to create a new tag payload."
    exit 1
  fi
  assert_json 'data[-1]["payloadJson"]["tagId"] == 1 and data[-1]["acknowledged"] is False' \
    "Latest payload after product update was not stored as pending for tag 1"

  log "Checking explicit tag publish contract"
  request POST /api/tags/1/publish
  assert_status 200
  assert_json 'data["status"] == "published" and data["tagId"] == 1 and data["payload"]["tagId"] == 1' \
    "Unexpected response from POST /api/tags/1/publish"

  request GET /api/tag-payloads
  assert_status 200
  after_publish_count="$(json_query 'len(data)')"
  if (( after_publish_count <= after_patch_count )); then
    echo "Expected explicit publish to create another tag payload."
    exit 1
  fi
  assert_json 'data[-1]["payloadJson"]["tagId"] == 1 and data[-1]["acknowledged"] is False' \
    "Latest payload after explicit publish was not pending for tag 1"

  log "Checking MQTT ACK handling"
  publish_mqtt_json "b-g/tag1/ack" "{'tagId': 1, 'ack': True}"
  sleep 1

  request GET /api/tag-payloads
  assert_status 200
  assert_json 'data[-1]["payloadJson"]["tagId"] == 1 and data[-1]["acknowledged"] is True' \
    "Latest payload for tag 1 was not acknowledged after ACK publish"

  log "Checking MQTT advertisement to DB and Socket.IO flow"
  socket_log="$(mktemp)"
  start_socket_listener "$socket_log"
  sleep 1

  publish_mqtt_json "b-g/tag1/advertisement" "{'battery': 42, 'rssi': -62}"
  wait_for_pid "$SOCKET_LISTENER_PID" "$socket_log"

  request GET "/battery?tagId=1"
  assert_status 200
  assert_json 'data["battery"] == 42' "Battery value was not updated from advertisement message"

  LAST_BODY="$(cat "$socket_log")"
  assert_json 'data["tagId"] == 1 and data["batteryPct"] == 42 and data["status"] in {"active", "low-battery", "offline"}' \
    "Socket.IO battery_update payload did not match contract"
  rm -f "$socket_log"

  log "Backend integration contract smoke test passed"
}

main "$@"
