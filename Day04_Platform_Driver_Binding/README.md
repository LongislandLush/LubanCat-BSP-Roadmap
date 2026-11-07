# Day04 — Platform Device & Driver Binding

## 1. Objective

Understand how Linux represents Device Tree hardware nodes as Platform Devices and how to inspect their currently bound drivers through sysfs.

This lab focuses on observing an existing driver binding, rather than implementing a new Linux kernel driver.

## 2. Environment

| Item | Configuration |
|---|---|
| Board | Embedfire LubanCat 5 V2 |
| SoC | Rockchip RK3588 |
| Architecture | AArch64 |
| Linux Kernel | 6.1.118 |
| OS | Ubuntu 26.04 LTS |
| Interface | Linux Shell |
| Script | `trace_binding.sh` |

## 3. Directory Structure

```text
Day04_Platform_Driver_Binding/
├── trace_binding.sh
└── README.md
```

## 4. Implementation

The `trace_binding.sh` script:

1. Searches `/sys/bus/platform/devices/` for a Platform Device.
2. Selects a device with a readable Device Tree `compatible` property and an existing driver binding.
3. Reads the corresponding Device Tree node through `of_node`.
4. Decodes NUL-separated `compatible` strings.
5. Resolves the `driver` symbolic link to identify the currently bound driver.
6. Reports an error and returns a nonzero exit status when the requested device does not exist.

### Run

```bash
bash trace_binding.sh
```

## 5. Hardware Verification

The script was executed on LubanCat 5 V2.

### Test 1 — Platform Driver Binding

Command:

```bash
bash trace_binding.sh
```

Actual output:

```text
=== Platform Driver Binding ===
Device: 10f000.sram
Device Tree node:
/sys/firmware/devicetree/base/sram@10f000
Compatible strings:
mmio-sram
Bound driver:
sram
```

**Result: PASS**

The script successfully identified a Platform Device, its Device Tree node, the `compatible` property, and its currently bound driver.

### Test 2 — Invalid Device Path

Command:

```bash
bash trace_binding.sh \
  /sys/bus/platform/devices/not-a-real-device

echo "Exit status: $?"
```

Actual output:

```text
ERROR: platform device not found
Exit status: 2
```

**Result: PASS**

The script correctly rejected a nonexistent device path and returned exit status `2`.

## 6. Key Findings

### Device Tree and Platform Device

The Device Tree node:

```text
/sys/firmware/devicetree/base/sram@10f000
```

is associated with the Linux Platform Device:

```text
/sys/bus/platform/devices/10f000.sram
```

Its `compatible` property contains:

```text
mmio-sram
```

### Driver Binding

The Platform Device's `driver` symbolic link resolves to the driver named:

```text
sram
```

This confirms that the device is currently bound to the `sram` driver.

However, the experiment does not directly inspect the driver's `of_match_table` or trace its `probe()` execution.

### Sysfs as a Debugging Interface

The Linux sysfs interface provides useful information for inspecting the relationship between devices, firmware descriptions, and drivers without modifying the kernel.

## 7. Verification Summary

| Test | Result |
|---|---|
| Discover Platform Device | PASS |
| Read Device Tree node | PASS |
| Read `compatible` | PASS |
| Identify bound driver | PASS |
| Reject invalid device path | PASS |
| Verify nonzero error exit status | PASS |

## 8. Limitations

This lab does not cover:

- Writing a custom Platform Driver
- Inspecting the driver's complete match table
- Tracing `probe()` execution
- Driver unbinding or rebinding
- Kernel module development

All operations in this lab are read-only.

## 9. Status

**PASS — 2026-11-07**

Completed the Day04 practical exercise originally scheduled for 2026-11-02, including the invalid-device boundary test.
