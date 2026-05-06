#!/bin/sh

if [ -z "${MQTT_BROKER:-}" ]; then
  echo "MQTT_BROKER must be set to the broker IP or hostname reachable from the Raspberry Pi."
  exit 1
fi

docker run --rm \
--privileged \
--network host \
-v /var/run/dbus:/var/run/dbus \
-e GATEWAY_MODE=mqtt \
-e MQTT_BROKER="${MQTT_BROKER:-mosquitto}" \
-e MQTT_PORT=1883 \
esl-gateway
