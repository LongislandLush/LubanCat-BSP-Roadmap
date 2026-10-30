# Day03 — Linux Process, PID, PPID & systemd

**Project:** LubanCat BSP Roadmap 2.0  
**Board:** LubanCat-5 V2 (RK3588)  
**OS:** Ubuntu 26.04 ARM64  
**Kernel:** 6.1.118  
**Status:** Lab01 and Lab02 PASS

## Learning objectives

- Identify PID 1, a shell PID and its parent PID (PPID).
- Inspect `/proc/<PID>` and distinguish permission errors from missing files.
- Understand systemd `.service` and `.socket` units and socket activation.
- Distinguish unit load, active and enable states; read unit dependencies.

## Lab01 — PID, PPID and `/proc`

### Commands

```bash
ps -p 1 -o pid,ppid,comm,args
readlink -f /proc/1/exe
grep -E '^(Name|State|Pid|PPid):' /proc/1/status
echo "Shell PID = $$"
ps -o pid,ppid,comm -p $$
ps -ef | grep '[s]shd'
ls -l /proc/1/exe
ps -p 1784 -o pid,ppid,comm,args
sudo readlink /proc/1/exe
```

### Observed results

```text
PID  PPID  COMMAND  COMMAND
1    0     systemd  /sbin/init splash #jia-04/21/2026

Name: systemd
State: S (sleeping)
Pid: 1
PPid: 0

Shell PID = 2572
PID   PPID  COMMAND
2572  1784  bash

PID   PPID  COMMAND  COMMAND
1784  1     login    login -- leon

ls: cannot open file '/proc/1/exe': Permission denied
sudo readlink /proc/1/exe -> /usr/lib/systemd/systemd
```

- PID 1 is `systemd`; PPID 0 is expected for PID 1.
- `S` means interruptible sleep; it does not imply a crash.
- The observed process relationship is `systemd (1) → login (1784) → bash (2572)`. This is not proof of an SSH session.
- Resolving `/proc/1/exe` as an ordinary user failed due to access restrictions; `sudo readlink` confirmed the executable path. Permission denied is not the same as file not found.
- The `ps ... grep '[s]shd'` command produced no matching processes in that snapshot.

## Lab02 — systemd units and SSH socket activation

### Commands

```bash
systemctl status ssh --no-pager
systemctl status ssh.socket --no-pager
systemctl is-enabled ssh.service ssh.socket
systemctl is-active ssh.service ssh.socket
systemctl cat ssh.socket
systemctl cat ssh.service
systemctl show ssh.socket -p Triggers
systemctl show ssh.service -p TriggeredBy
```

### Observed unit states

```text
ssh.service: disabled / inactive
ssh.socket: enabled / active (listening)
ssh.socket: Listen 0.0.0.0:22 and [::]:22 (TCP)
Triggers=ssh.service
TriggeredBy=ssh.socket
```

### Relevant `ssh.socket` configuration

```ini
[Unit]
Description=OpenBSD Secure Shell server socket
Before=sockets.target ssh.service
ConditionPathExists=!/etc/ssh/sshd_not_to_be_run

[Socket]
ListenStream=0.0.0.0:22
ListenStream=[::]:22
BindIPv6Only=ipv6-only
Accept=no
FreeBind=yes

[Install]
WantedBy=sockets.target
RequiredBy=ssh.service
```

### Relevant `ssh.service` configuration

```ini
[Unit]
After=network.target nss-user-lookup.target auditd.service
ConditionPathExists=!/etc/ssh/sshd_not_to_be_run

[Service]
EnvironmentFile=-/etc/default/ssh
ExecStartPre=/usr/sbin/sshd -t
ExecStart=/usr/sbin/sshd -D $SSHD_OPTS
ExecReload=/usr/sbin/sshd -t
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
RestartPreventExitStatus=255
Type=notify
RuntimeDirectory=sshd
RuntimeDirectoryMode=0755

[Install]
WantedBy=multi-user.target
Alias=sshd.service
```

### Interpretation

- `ssh.socket` listens on TCP port 22; when appropriate, systemd can activate `ssh.service` to handle connections.
- `Accept=no` means the socket activates a shared service rather than a separate service instance for each accepted connection.
- `ExecStartPre=/usr/sbin/sshd -t` validates SSH server configuration before startup.
- `ExecStart=/usr/sbin/sshd -D $SSHD_OPTS` starts `sshd` in foreground mode for service management.
- `WantedBy=` and `RequiredBy=` are installation relationships used by `systemctl enable`; they do not directly report whether a unit is currently active.
- `Before=` and `After=` express ordering; `Wants=` and `Requires=` express dependency relationships.
- `disabled` does not mean prohibited: another unit may still trigger or start the service.
- `stop` stops a unit now; `disable` removes its enable-created links; `mask` prevents ordinary activation until unmasked. Stopping `ssh.socket` does not permanently prohibit future startup.

## Understanding checks

1. `echo $$` in an interactive Bash session identifies the current shell's PID — **PASS**.
2. `ssh.service` can be inactive while `ssh.socket` listens and triggers it — **PASS**.
3. Stopping `ssh.socket` does not permanently disable or mask it; it can be started again — **PASS**.

## Safety and scope

All experiments were read-only. No SSH services or sockets were stopped, disabled, masked, or reconfigured. PID values are snapshots and may change after reboot or re-login.

## Next lab

Day04: process states, signals and safe service observation (without stopping remote access services).
