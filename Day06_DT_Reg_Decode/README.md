# Day06 — Device Tree `reg` Property Decoding

**Project:** LubanCat BSP Roadmap  
**Board:** EmbedFire LubanCat-5 V2  
**SoC:** Rockchip RK3588  
**Architecture:** ARM64 (AArch64)  
**Kernel:** Linux 6.1.118  
**Status:** PASS  
**Date:** 2026-11-09

## 1. Objective

Read and decode the `reg` property of a real Device Tree node on the RK3588 platform.

The goal is to understand how Device Tree represents hardware address and size information using 32-bit cells, and how software can reconstruct the values.

This lab builds upon Day04, which inspected Linux platform device and driver binding.

## 2. Environment

| Item | Configuration |
|---|---|
| Development board | LubanCat-5 V2 |
| SoC | Rockchip RK3588 |
| Operating system | Ubuntu ARM64 |
| Kernel | Linux 6.1.118 |
| Language | Python 3 |
| Target device | `10f000.sram` |
| Device Tree node | `sram@10f000` |
| Interface | `/sys/bus/platform/devices/` |

All operations in this lab are read-only. No hardware registers, Device Tree files, or kernel drivers were modified.

## 3. Target Device Tree Node

The target platform device was previously identified during Day04:

```text
Platform device: 10f000.sram
Device Tree node: sram@10f000
Compatible: mmio-sram
Bound driver: sram
```

The Device Tree node is accessible through:

```bash
/sys/bus/platform/devices/10f000.sram/of_node
```

The `reg` property describes address and size information in the parent bus address space.

## 4. Implementation

The Python script `decode_reg.py`:

1. Locates the specified Device Tree node.
2. Reads `#address-cells` and `#size-cells` from its parent node.
3. Reads the binary `reg` property.
4. Decodes 32-bit big-endian cells.
5. Combines cells into address and size values.
6. Reports invalid or missing nodes using a nonzero exit status.

The default target is:

```text
/sys/bus/platform/devices/10f000.sram/of_node
```

### Run the decoder

```bash
python3 decode_reg.py
echo "Exit status: $?"
```

## 5. Hardware Verification

### Test 1 — Decode a valid Device Tree node

**Actual output:**

```text
Node: sram@10f000
Parent cells: address=2, size=2
reg[0]: bus_address=0x10f000, size=0x100 (256 bytes)
Exit status: 0
```

**Result: PASS**

The parent node uses:

- `#address-cells = 2`
- `#size-cells = 2`

Each cell is 32 bits, so each address and size field occupies two cells.

The decoded values are:

| Property | Value |
|---|---|
| Address | `0x10F000` |
| Size | `0x100` |
| Size in decimal | 256 bytes |
| Exit status | 0 |

The decoded values are equivalent to the following cell representation:

```dts
reg = <0x00000000 0x0010f000
       0x00000000 0x00000100>;
```

This is a reconstructed representation of the decoded values, not a direct copy of the original DTS source.

### Test 2 — Invalid Device Tree node

**Command:**

```bash
python3 decode_reg.py \
  /sys/bus/platform/devices/not-a-real-device

echo "Exit status: $?"
```

**Actual output:**

```text
ERROR: device-tree node not found
Exit status: 2
```

**Result: PASS**

The decoder detected the missing node and returned the expected exit status without an unhandled Python exception.

## 6. Key Findings

### 6.1 Device Tree uses big-endian cells

Device Tree properties are stored as binary data.

Address and size fields can span multiple 32-bit cells.

For this device, both fields occupy 64 bits.

### 6.2 `reg` does not directly represent a C pointer

The decoded address is expressed in the parent bus address space.

A Linux kernel driver must obtain and map hardware resources appropriately before accessing memory-mapped registers.

The value must not be directly cast to a pointer and dereferenced.

### 6.3 Bus address translation matters

A Device Tree `reg` address is not necessarily identical to the final CPU physical address.

The parent bus hierarchy and properties such as `ranges` may affect address translation.

This lab decoded the raw `reg` property but did not independently validate the complete bus-to-CPU address translation.

### 6.4 Input validation is important

The decoder rejects nonexistent nodes with an explicit error message and exit status.

This reinforces the input-validation concepts practiced in earlier C buffer parsing exercises.

## 7. Limitations

The following were not tested:

- Full Device Tree address translation through `ranges`
- Multiple `reg` entries on different device nodes
- Kernel resource acquisition through `platform_get_resource()`
- MMIO mapping through `devm_platform_ioremap_resource()`
- Direct hardware register access
- Malformed binary `reg` property test cases

The script is intended as a learning tool rather than a complete Device Tree address translation implementation.

## 8. Verification Summary

| Test | Result |
|---|---|
| Valid Device Tree node decoding | PASS |
| Parent address-cell decoding | PASS |
| Parent size-cell decoding | PASS |
| Address and size reconstruction | PASS |
| Invalid node handling | PASS |
| Expected exit status validation | PASS |

**Final result: PASS — RK3588 hardware verification completed.**

## 9. Next Learning Direction

This lab establishes the relationship between Device Tree resource descriptions and hardware address information.

Future BSP and Linux driver exercises may explore:

- Platform driver resource acquisition
- Device Tree bus address translation
- Kernel MMIO mapping
- The relationship between physical and kernel virtual addresses

These topics are future learning directions and are not part of the current lab's verified results.
