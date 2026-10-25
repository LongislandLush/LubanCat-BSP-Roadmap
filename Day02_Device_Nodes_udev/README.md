# Day02 — Device Nodes, Major/Minor & udev

**Board:** LubanCat-5 V2 (RK3588)  
**OS:** Ubuntu 26.04 ARM64 | **Kernel:** 6.1.118  
**Status:** Lab01 / Lab02 PASS

## Lab01 — Character Device / Major / Minor

Commands:
```bash
ls -l /dev/null
ls -l /dev/zero
ls -l /dev/ttyFIQ0
```

Observed:
```text
crw-rw-rw- 1 root root   1, 3 /dev/null
crw-rw-rw- 1 root root   1, 5 /dev/zero
crw------- 1 leon tty 253, 0 /dev/ttyFIQ0
```

`c` denotes a character device. The numbers represent **major/minor**, not USB bus/port. A shared major with different minors can distinguish logical functions, not necessarily different physical devices.

## Lab02 — devtmpfs / udev / sysfs

Commands:
```bash
findmnt /dev
systemctl is-active systemd-udevd
ls -l /dev/ttyFIQ0
cat /sys/class/tty/ttyFIQ0/dev
udevadm info --query=property --name=/dev/ttyFIQ0
```

Observed:
```text
/dev  udev  devtmpfs  rw,nosuid,relatime,...
systemd-udevd: active
/dev/ttyFIQ0: character device 253,0
/sys/class/tty/ttyFIQ0/dev: 253:0

DEVPATH=/devices/platform/fiq_debugger.0/tty/ttyFIQ0
DEVNAME=/dev/ttyFIQ0
MAJOR=253
MINOR=0
SUBSYSTEM=tty
USEC_INITIALIZED=6892092
ID_MM_CANDIDATE=1
TAGS=:systemd:
CURRENT_TAGS=:systemd:
```

**Interpretation:** `/dev` uses devtmpfs (`SOURCE=udev` is a mount label). `systemd-udevd` is active and processes device events/rules, but this alone does not prove it created this node. The `253:0` sysfs property matches `/dev/ttyFIQ0`'s device number. `DEVPATH` locates it under the kernel's `fiq_debugger.0` platform device.

```text
Kernel device model: fiq_debugger.0
  └── TTY: ttyFIQ0
      ├── /sys/class/tty/ttyFIQ0 (dev=253:0)
      └── /dev/ttyFIQ0 (character device 253,0)
```

## Understanding checks

- `/dev/null` major 1, minor 3; `/dev/zero` major 1, minor 5.
- Major/minor values are not USB bus/port numbers.
- Multiple minors under one major may represent multiple functions of one driver.
- devtmpfs provides basic device nodes; udev processes events, permissions and rules.
- Not finding a character device under `/sys/class/tty` does **not** imply a broken driver: it might belong to another class. A manually created node may also lack a working driver.

## Scope and next steps

All commands were read-only. No drivers, udev rules or device nodes were modified. Next: inspect `/sys/dev/char/253:0`, compare block/character devices and explore uevents.

## Commit

```bash
git add Day02_Device_Nodes_udev/README.md
git commit -m "docs: complete Day02 device nodes and udev labs"
git push
```
