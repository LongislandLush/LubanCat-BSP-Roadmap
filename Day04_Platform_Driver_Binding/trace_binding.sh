#!/usr/bin/env bash
set -euo pipefail

SYSFS=/sys/bus/platform/devices
DEVICE="${1:-}"

# Automatically select a bound DT platform device.
if [[ -z "$DEVICE" ]]; then
    for path in "$SYSFS"/*; do
        if [[ -d "$path" &&
              -r "$path/of_node/compatible" &&
              -L "$path/driver" ]]; then
            DEVICE="$path"
            break
        fi
    done
fi

if [[ -z "$DEVICE" || ! -d "$DEVICE" ]]; then
    echo "ERROR: platform device not found" >&2
    exit 2
fi

if [[ ! -r "$DEVICE/of_node/compatible" ]]; then
    echo "ERROR: DT compatible unavailable" >&2
    exit 3
fi

echo "=== Platform Driver Binding ==="

echo "Device: $(basename "$DEVICE")"

echo "Device Tree node:"
readlink -f "$DEVICE/of_node"

echo "Compatible strings:"
tr '\0' '\n' < "$DEVICE/of_node/compatible"

if [[ -L "$DEVICE/driver" ]]; then
    echo "Bound driver:"
    basename "$(readlink -f "$DEVICE/driver")"
else
    echo "Bound driver: (none)"
fi
