# Day05 — Linux Memory & Virtual Address Space

**Project:** LubanCat BSP Roadmap 2.0  
**Board:** LubanCat-5 V2 (RK3588)  
**OS:** Ubuntu 26.04 ARM64  
**Kernel:** 6.1.118  
**Status:** Lab01 / Lab02 PASS (hardware observations recorded)

## Objectives

- Distinguish virtual addresses from physical addresses and understand per-process mappings.
- Interpret `free -h`, `/proc/meminfo`, and `/proc/<PID>/maps`.
- Observe global, static, stack, and dynamically allocated objects in a C program.
- Compare addresses between executions as evidence consistent with ASLR.

## Lab01 — System memory and Bash mappings

Commands:

```bash
free -h
head -n 12 /proc/meminfo
echo $$
head -n 20 /proc/$$/maps
grep -E '\[heap\]|\[stack\]' /proc/$$/maps
```

### Observations

| Metric | Observed |
| --- | ---: |
| RAM total (`free -h`) | 7.7 GiB |
| RAM used | 699 MiB |
| RAM free | 6.3 GiB |
| Buff/cache | 923 MiB |
| RAM available | 7.0 GiB |
| Swap total / used | 2.0 GiB / 0 B |
| `/proc/meminfo` MemTotal | 8,105,196 kB |
| MemFree | 6,587,384 kB |
| MemAvailable | 7,387,108 kB |
| Buffers | 29,176 kB |
| Cached | 840,464 kB |
| Bash PID | 2586 |

Selected Bash mappings:

```text
aaaad0d49000-aaaad1000000 rw-p ... [heap]
fffffdc58000-fffffdc79000 rw-p ... [stack]
```

The mapped heap range is `0x2B7000` bytes (approximately 2.71 MiB); the stack range is `0x21000` bytes (132 KiB). **Mapping size is not the same as resident physical RAM usage.** `MemAvailable` accounts for memory the kernel estimates can be reclaimed and is not additive with `free` and cache.

## Lab02 — C memory layout

Source: [`memory_lab.c`](./memory_lab.c)

Compile and run on the board:

```bash
gcc -Wall -Wextra -O0 -g memory_lab.c -o memory_lab
./memory_lab
```

The program prints its PID and variable addresses, then waits for Enter so a second terminal can inspect `/proc/<PID>/maps`.

### Observed addresses

| Object | PID 3775 | PID 4109 |
| --- | --- | --- |
| `global_init` | `0xaaaae9310010` | `0xaaaad3c50010` |
| `global_uninit` | `0xaaaae931001c` | `0xaaaad3c5001c` |
| `static_var` | `0xaaaae9310014` | `0xaaaad3c50014` |
| `local_var` | `0xfffff799c72c` | `0xffffe510a96c` |
| `&heap_var` | `0xfffff799c730` | `0xffffe510a970` |
| `heap_var` (malloc return) | `0xaaab1dddb010` | `0xaaaafbf4f010` |
| `*heap_var` | `30` | `30` |

Second terminal (while PID 4109 was still running):

```bash
PID=4109
grep -E 'memory_lab|\[heap\]|\[stack\]|libc.so' /proc/$PID/maps
```

Relevant PID 4109 mappings:

```text
aaaad3c30000-aaaad3c31000 r-xp ... /home/leon/LubanCat-BSP-Roadmap/Day05_Linux_Memory/memory_lab
aaaad3c4f000-aaaad3c50000 r--p ... /home/leon/LubanCat-BSP-Roadmap/Day05_Linux_Memory/memory_lab
aaaad3c50000-aaaad3c51000 rw-p ... /home/leon/LubanCat-BSP-Roadmap/Day05_Linux_Memory/memory_lab
aaaafbf4f000-aaaafc000000 rw-p ... [heap]
ffffa7950000-ffffa7af9000 r-xp ... /usr/lib/aarch64-linux-gnu/libc.so.6
ffffe50eb000-ffffe510c000 rw-p ... [stack]
```

### Mapping verification

A mapped address belongs to a region when `start <= address < end`.

- `global_init`, `global_uninit`, `static_var` are all inside `0xaaaad3c50000–0xaaaad3c51000` (`rw-p`, executable file mapping).
- `local_var` and `&heap_var` are inside `0xffffe50eb000–0xffffe510c000` (`[stack]`).
- The pointer **value** `heap_var = 0xaaaafbf4f010` is inside `0xaaaafbf4f000–0xaaaafc000000` (`[heap]`), 16 bytes from its start.
- `&heap_var` is the address of the local pointer variable; `heap_var` is the address returned by `malloc`. These are distinct concepts.

The three globals/static objects were observed in the same writable mapping. The mapping alone does not identify exact ELF sections; `.data` and `.bss` can be examined separately with ELF tools if needed.

### ASLR observation

Global, stack, and allocated-object addresses differed between runs (PID 3775 vs 4109), consistent with address-space layout randomization (ASLR). This comparison observes address changes; it does not independently establish the current ASLR policy. A separate read-only check would be `cat /proc/sys/kernel/randomize_va_space`.

## Key takeaways

1. Linux user-space pointers are virtual addresses; do not treat them as physical or DMA addresses.
2. `/proc/<PID>/maps` reports mapped virtual address ranges and permissions (`r`, `w`, `x`, `p`/`s`).
3. A pointer stored on the stack may point to an allocation in the heap.
4. A virtual mapping's size is not equivalent to its resident RAM consumption.
5. Separate process launches may receive different virtual addresses due to ASLR.

## Validation and repository hygiene

- [x] Lab01 memory commands inspected on the LubanCat.
- [x] `memory_lab.c` compiled with GCC and ran successfully.
- [x] Global/static, stack, and heap addresses matched PID 4109 mappings.
- [x] Addresses compared across two runs.
- [ ] README and source committed and pushed (complete using Git commands below).

Recommended `.gitignore` entry (repository root) to avoid committing the compiled executable:

```gitignore
/Day05_Linux_Memory/memory_lab
```

Suggested Git commands:

```bash
cd ~/LubanCat-BSP-Roadmap
git status --short
git add Day05_Linux_Memory/README.md Day05_Linux_Memory/memory_lab.c
# Optionally add the ignore rule to the root .gitignore before staging it.
git diff --cached --stat
git commit -m "lab: verify Day05 Linux memory mappings"
git push origin main
git status
```
