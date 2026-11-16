# Day07 — Platform Resource Inspection

**Board:** LubanCat-5 V2 / RK3588  
**Kernel:** Linux 6.1.118 (previously recorded)  
**Status:** PARTIAL PASS  
**Date:** 2026-11-16

## Objective

Inspect a real Linux platform device, its Device Tree association, driver binding, and resource visibility through sysfs.

## Implementation

Script: `inspect_resource.py`

The script checks the platform device, resolves its Device Tree node and bound driver, and attempts to inspect a sysfs `resource` file when available.

## Hardware Results

```text
Device: 10f000.sram
DT Node: /sys/firmware/devicetree/base/sram@10f000
Driver: sram
Resource: not exposed through sysfs
Exit status: 0
```

## Boundary Test

```text
ERROR: platform device not found
Exit status: 2
```

**Result: PASS**

## Findings

- The platform device exists and is bound to the `sram` driver.
- The inspected sysfs path does not expose a `resource` file.
- The absence of this file does not establish that the kernel device has no resources.
- The Device Tree `reg` value from Day06 describes a bus address and size; it is not directly usable as a C pointer.
- Kernel drivers normally acquire resources and use appropriate MMIO mapping APIs before accessing hardware.

## Limitations

The following have not been verified:

- Kernel-side platform resource start/end values
- Complete Device Tree address translation
- MMIO mapping through kernel APIs
- Hardware register access

## Conclusion

**PARTIAL PASS:** Device identification, driver binding, and invalid-device handling were verified on real hardware. Kernel resource range comparison remains unverified.