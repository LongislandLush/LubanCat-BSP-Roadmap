# Day01｜Linux Filesystem & Kernel Interface

- 日期：2026-10-21（Roadmap 2.0）
- Board：Embedfire LubanCat-5 V2 / RK3588
- OS：Ubuntu 26.04 LTS ARM64
- Kernel：6.1.118
- Status：PASS（Lab01、Lab02；理解驗收 3/3）

## 1. 學習目標

1. 區分 SD 卡 ext4 RootFS 與虛擬檔案系統 procfs、sysfs。
2. 理解 Linux 主要目錄、Symbolic Link、Kernel runtime 資訊。
3. 透過 sysfs 追蹤 `wlan0` → USB Interface → Driver Binding。
4. 分辨 USB Device、Interface、Host Controller、Network Interface。

## 2. Lab01｜Filesystem 與 Kernel 資訊

### 指令

```bash
pwd
ls -lah /
findmnt /
findmnt /proc
findmnt /sys
cat /proc/version
cat /proc/uptime
head -n 8 /proc/meminfo
```

### 實測結果

```text
pwd                    /home/leon
/                      /dev/mmcblk1p2 ext4 rw,relatime
/proc                  proc procfs
/sys                   sysfs sysfs
Kernel                 Linux 6.1.118 / aarch64
/proc/uptime           3345.59 26641.29
MemTotal               8105196 kB
MemFree                6640044 kB
MemAvailable           7408012 kB
Cached                 797852 kB
```

- `/proc`、`/sys` 的掛載點目錄可以位於 RootFS，但掛載後的內容由 Kernel 動態提供，不是 SD 卡上一般檔案。
- `/bin -> usr/bin`、`/lib -> usr/lib`、`/sbin -> usr/sbin`：merged-/usr 佈局中的 symbolic links。
- `/proc/uptime` 第一欄約 55 分 45.59 秒；第二欄是所有 CPU 累積 idle time，不是第二個 uptime。
- `MemTotal` 約 7.73 GiB，少於標稱 8 GiB，可能涉及保留記憶體等；這份資料無法單獨確定差額組成。
- `MemAvailable` 比 `MemFree` 更適合估計新程式可用記憶體。

## 3. Lab02｜sysfs、USB Device Model 與 Driver Binding

### 指令

```bash
readlink -f /sys/class/net/wlan0/device
readlink -f /sys/class/net/wlan0/device/driver
ls -lah /sys/class/net/wlan0/
lsusb -t
ethtool -i wlan0
```

### 實測結果

```text
/sys/class/net/wlan0/device
  -> /sys/devices/platform/fc880000.usb/usb4/4-1/4-1.3/4-1.3:1.2
/sys/class/net/wlan0/device/driver
  -> /sys/bus/usb/drivers/rtl8821cu
```

USB topology：

```text
fc880000.usb (EHCI Host Controller)
└── USB Bus 004 (480M)
    └── 4-1 (USB Hub, 4 ports)
        └── 4-1.3 (Realtek composite USB device)
            ├── Interface 0 → btusb
            ├── Interface 1 → btusb
            └── Interface 2 → rtl8821cu → wlan0
```

`ethtool -i wlan0`：

```text
driver: rtl8821cu
version: v5.12.0.4-1-g9241a6516.20210916
firmware-version: 24.8
bus-info: 4-1.3:1.2
```

- `4-1.3:1.2`：Bus 4、Port 1 的 Hub 下游 Port 3、Configuration 1、Interface 2；`:1.2` 不是 USB 1.2 版本。
- `lsusb -t` 的 `480M` 是 USB 2.0 High-Speed 的標稱連線速率，不是 Wi-Fi 實際吞吐量。
- 一個 USB composite device 可以有多個 interface，各自綁定不同 Driver。
- USB 拔除時，USB core 通知驅動清理，通常 `wlan0` 及 `/sys/class/net/wlan0` 會消失；不等於 Kernel Module 一定卸載。未實際拔除測試。

## 4. 理解驗收

- Q1：`/proc`、`/sys` 主要由誰提供？→ Kernel（正確）
- Q2：`findmnt /` 確認什麼？→ RootFS 掛載來源（正確）
- Q3：Kernel 記憶體資訊在哪裡？→ `/proc/meminfo`（正確）
- Lab02：拔掉 Wi-Fi Dongle，`/sys/class/net/wlan0` 通常如何？→ 消失（正確；原因是裝置移除與 netdev 註銷）

## 5. 與 BSP / Driver 工作的連結

`wlan0` 是網路子系統暴露的介面；`4-1.3:1.2` 是 USB interface；`rtl8821cu` 是綁定該 interface 的 Kernel driver。這條路徑把 user space 可見的名稱與 Kernel Device Model 串起來。

## 6. 待辦與限制

- Day00 的 `apt upgrade` 尚未執行；`NetworkManager-wait-online.service` 曾失敗，但 Wi-Fi 後來正常連線。
- 先前 USB3 Type-A 供電異常原因仍未確認；本日沒有對故障埠做測試。
- 下一個 Lab：`/dev`、udev、device node、major/minor 與 sysfs 的差別。

## 7. 今日一句話

> 不只確認 `wlan0` 存在，還能用 sysfs、`lsusb -t`、`ethtool` 追到 USB Interface 與 `rtl8821cu` Driver。
