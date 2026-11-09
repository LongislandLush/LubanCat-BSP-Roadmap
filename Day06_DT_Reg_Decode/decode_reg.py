#!/usr/bin/env python3

import struct
import sys
from pathlib import Path

node = Path(
    sys.argv[1] if len(sys.argv) > 1
    else "/sys/bus/platform/devices/10f000.sram/of_node"
)

if not node.is_dir():
    print("ERROR: device-tree node not found", file=sys.stderr)
    sys.exit(2)

node = node.resolve()


def cell_count(key, default):
    prop = node.parent / key
    raw = prop.read_bytes() if prop.exists() else b""

    if not raw:
        return default

    if len(raw) != 4:
        raise ValueError(f"invalid {key}")

    return int.from_bytes(raw, "big")


try:
    addr_n = cell_count("#address-cells", 2)
    size_n = cell_count("#size-cells", 1)

    raw = (node / "reg").read_bytes()

    width = addr_n + size_n

    if addr_n < 1 or not raw or len(raw) % (width * 4):
        raise ValueError("invalid reg layout")

    cells = struct.unpack(f">{len(raw)//4}I", raw)

    print(f"Node: {node.name}")
    print(f"Parent cells: address={addr_n}, size={size_n}")

    for i in range(0, len(cells), width):
        address = 0
        size = 0

        for value in cells[i:i + addr_n]:
            address = (address << 32) | value

        for value in cells[i + addr_n:i + width]:
            size = (size << 32) | value

        print(
            f"reg[{i//width}]: "
            f"bus_address=0x{address:x}, "
            f"size=0x{size:x} ({size} bytes)"
        )

except (OSError, ValueError) as exc:
    print(f"ERROR: {exc}", file=sys.stderr)
    sys.exit(3)
