#!/usr/bin/env bash
set -euo pipefail

echo "Starting services..."
docker compose up -d postgres mosquitto backend

echo "Waiting for backend..."
until curl -sf http://localhost:5000/ >/dev/null; do
  sleep 1
done

echo "Updating seeded product..."
curl -s -X PATCH http://localhost:5000/api/products/1 \
  -H 'Content-Type: application/json' \
  -d '{"price":23.4}' >/tmp/product-update.json

echo "Checking pending payload..."
payloads_before="$(curl -s http://localhost:5000/api/tag-payloads)"
echo "$payloads_before"

echo "Publishing ACK..."
docker compose exec -T backend python -c "import json; import paho.mqtt.client as mqtt; client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2); client.connect('mosquitto', 1883, 60); client.publish('g-b/tag1/ack', json.dumps({'ack': True})); client.disconnect()"

sleep 1

echo "Checking acknowledged payload..."
payloads_after="$(curl -s http://localhost:5000/api/tag-payloads)"
echo "$payloads_after"
