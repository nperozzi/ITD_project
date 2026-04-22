#!/bin/sh
docker run --rm \
  --privileged \
  --network host \
  -v /var/run/dbus:/var/run/dbus \
  -e GATEWAY_MODE=mqtt \
  -e MQTT_BROKER=192.168.1.229 \
  -e MQTT_PORT=1883 \
  esl-gateway
