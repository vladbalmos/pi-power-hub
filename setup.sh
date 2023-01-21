#!/bin/bash

mkdir -p src/lib
touch src/lib/__init__.py
cp  -r lib/micropython-async/v3/{primitives,threadsafe} src/lib
rm -rf src/lib/primitives/tests
