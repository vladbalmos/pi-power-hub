#!/bin/bash

mkdir -vp src/lib
touch src/lib/__init__.py
cp  -vr lib/micropython-async/v3/{primitives,threadsafe} src/lib
cp -v lib/micropython-mqtt/mqtt_as/mqtt_as.py src/lib
rm -vrf src/lib/primitives/tests
