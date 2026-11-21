# Day06 — Device Tree Resources & Platform Driver Binding

**Project:** LubanCat BSP Roadmap 2.0  
**Board:** Embedfire LubanCat-5 V2 (Rockchip RK3588)  
**OS / Kernel:** Ubuntu ARM64 / Linux 6.1.118 (as previously reported)  
**Status:** Lab01A–E PASS — read-only investigation  
**Scope:** Device Tree description, platform-device association, driver binding, and kernel I/O memory resource registration

## 1. Problem

How can an Embedded Linux BSP engineer trace a hardware description from the running Device Tree to a Linux platform device, its bound driver, and the memory resource registered by the kernel—without writing hardware registers or changing the DTB?

This lab investigates the **`10f000.sram`** device on the RK3588-based LubanCat-5 V2.

## 2. Investigation

### 2.1 Confirm the running board description

Commands:

```bash
ls -ld /sys/firmware/devicetree/base
tr -d '\0' < /sys/firmware/devicetree/base/model; echo
tr '\0' '\n' < /sys/firmware/devicetree/base/compatible
```

Observed:

```text
Model: Embedfire LubanCat-5 V2
Compatible strings:
  embedfire,rk3588-lubancat-5-v2
  rockchip,rk3588
```

The Device Tree root was accessible at `/sys/firmware/devicetree/base`.

### 2.2 Locate a platform device and its OF node

The platform bus enumerated `10f000.sram` among other devices. Its `of_node` resolves to:

```text
/sys/firmware/devicetree/base/sram@10f000
```

The node's `compatible` property, decoded as a NUL-separated string list, was:

```text
mmio-sram
```

The device's `driver` symbolic link resolved to:

```text
/sys/bus/platform/drivers/sram
```

**Interpretation:** the kernel currently exposes a platform device associated with this Device Tree node, and the device is bound to the `sram` driver. The driver name does not have to equal the `compatible` string.

### 2.3 Decode `reg` using the parent's cell counts

Commands:

```bash
DEV=/sys/bus/platform/devices/10f000.sram
od -An -tx1 -v "$DEV/of_node/reg"
od -An -tu4 --endian=big "$DEV/of_node/../#address-cells"
od -An -tu4 --endian=big "$DEV/of_node/../#size-cells"
```

Observed:

```text
reg (raw bytes): 00 00 00 00 00 10 f0 00 00 00 00 00 00 00 01 00
#address-cells: 2
#size-cells:    2
```

Each cell is a big-endian 32-bit integer. Two address cells plus two size cells give one 16-byte address/size tuple:

```dts
reg = <0x0 0x0010f000 0x0 0x100>;
```

- Address as encoded in the root-level `reg`: **`0x0010F000`**
- Size: **`0x100` = 256 bytes**
- Inclusive end address: **`0x0010F0FF`** (`start + size - 1`)

This DTS snippet reconstructs the **observed property only**, not the complete original node.

### 2.4 Check the parent node and kernel resource registry

Observed parent:

```text
/sys/firmware/devicetree/base
```

There was **no `ranges` property** at this root node. This is not, by itself, evidence of a failed address translation: `sram@10f000` is a direct child of the Device Tree root. The independent kernel resource evidence below is decisive for the registered address range.

Attempting to read `/sys/bus/platform/devices/10f000.sram/resource` returned **No such file or directory**. A platform device is not guaranteed to expose such a sysfs file; its absence does not establish that the kernel lacks a resource.

Command:

```bash
sudo grep -i -E 'sram|10f000' /proc/iomem
```

Observed:

```text
0010f000-0010f0ff : 10f000.sram sram@10f000
ff001000-ff0effff : ff001000.sram sram@ff001000
```

The first line matches the decoded Device Tree address and size exactly. The second line is a **different SRAM resource** and is not evidence about the capacity or function of `10f000.sram`.

## 3. Verification

| Check | Observed evidence | Result |
|---|---|---|
| Running DT root | `/sys/firmware/devicetree/base` | PASS |
| Board identification | `Embedfire LubanCat-5 V2`, RK3588 compatibles | PASS |
| OF-linked platform device | `10f000.sram` → `/sram@10f000` | PASS |
| Device compatibility | `mmio-sram` | PASS |
| Driver binding | `driver` symlink → `sram` | PASS |
| `reg` decode | `0x0010F000`, `0x100` bytes (2+2 cells) | PASS |
| Kernel resource registration | `/proc/iomem`: `0010f000-0010f0ff` | PASS |
| SRAM functional read/write | Not attempted | NOT VERIFIED |
| Driver implementation/API | Source not inspected | NOT VERIFIED |

**Evidence chain:** Device Tree node → Platform Device → bound Platform Driver; Device Tree `reg` → matching kernel `/proc/iomem` entry. Binding and resource registration do **not** prove that every hardware operation works.

## 4. Engineering Value

1. **Device Tree parsing:** interpret `compatible` as a matching descriptor and `reg` as an address/size tuple governed by the parent node's `#address-cells` and `#size-cells`.
2. **Kernel device model:** use sysfs `of_node` and `driver` symlinks to distinguish a described device from a device actually bound to a driver.
3. **Resource debugging:** compare decoded `reg` with `/proc/iomem` rather than assuming every platform device has a sysfs `resource` file.
4. **Evidence discipline:** distinguish description, binding, and resource registration from actual device functionality.
5. **Future driver work:** these observations prepare for reading `platform_get_resource()`, managed MMIO mapping helpers, and the driver's `probe()` path; those APIs were **not** verified as used by this particular driver.

## 5. Reproducible Read-only Commands

```bash
DEV=/sys/bus/platform/devices/10f000.sram
tr -d '\0' < /sys/firmware/devicetree/base/model; echo
tr '\0' '\n' < /sys/firmware/devicetree/base/compatible
readlink -f "$DEV/of_node"
tr '\0' '\n' < "$DEV/of_node/compatible"
readlink "$DEV/driver"
od -An -tx1 -v "$DEV/of_node/reg"
od -An -tu4 --endian=big "$DEV/of_node/../#address-cells"
od -An -tu4 --endian=big "$DEV/of_node/../#size-cells"
sudo grep -i -E 'sram|10f000' /proc/iomem
```

**Safety:** Do not use `devmem`, modify the DTB, unbind/rebind the driver, or write to SRAM as part of this read-only lab.

## 6. Next Step

Archive this README in `Day06_Device_Tree_Resources/`, commit and push to the roadmap repository. Later, inspect the actual kernel driver source to study resource acquisition and mapping without assuming a specific API was used.
