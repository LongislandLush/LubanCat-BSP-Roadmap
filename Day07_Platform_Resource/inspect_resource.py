#!/usr/bin/env python3

import sys
from pathlib import Path

name = sys.argv[1] if len(sys.argv) > 1 else "10f000.sram"
device = Path("/sys/bus/platform/devices") / name

if not device.is_dir():
    print("ERROR: platform device not found")
    sys.exit(2)

print(f"Device: {name}")

of_node = device / "of_node"
driver = device / "driver"

if of_node.exists():
    print(f"DT Node: {of_node.resolve()}")
else:
    print("DT Node: unavailable")

if driver.exists():
    print(f"Driver: {driver.resolve().name}")
else:
    print("Driver: unbound")

resource = device / "resource"

if not resource.exists():
    print("Resource: not exposed through sysfs")
    sys.exit(0)

print("Resource entries:")

try:
    lines = resource.read_text().splitlines()

    for index, line in enumerate(lines):
        fields = line.split()

        if len(fields) != 3:
            print(f"  [{index}] unexpected format: {line}")
            continue

        start, end, flags = (
            int(value, 16) for value in fields
        )

        if end < start:
            print(f"  [{index}] invalid address range")
            continue

        size = end - start + 1

        print(
            f"  [{index}] "
            f"start=0x{start:x}, "
            f"end=0x{end:x}, "
            f"size=0x{size:x}, "
            f"flags=0x{flags:x}"
        )

except (OSError, ValueError) as exc:
    print(f"ERROR: {exc}")
    sys.exit(3)
