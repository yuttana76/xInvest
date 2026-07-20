# Checking Memory (RAM) Usage on Linux/Ubuntu

Here are the most common and useful commands to check memory (RAM) and swap usage on a Linux system.

---

## 1. Using `free` (Quickest & Easiest)
The `free` command displays the total amount of free and used physical and swap memory in the system.

Run:
```bash
free -h
```
*The `-h` option makes the output "human-readable" (showing values in GB, MB, etc.).*

### Expected Output
```text
               total        used        free      shared  buff/cache   available
Mem:           7.7Gi       3.1Gi       1.2Gi       250Mi       3.4Gi       4.1Gi
Swap:          2.0Gi       512Mi       1.5Gi
```
* **total:** Total installed RAM.
* **used:** Memory currently in use by processes.
* **free:** Memory completely unused.
* **buff/cache:** Memory used by the kernel for buffers and page cache (can be reclaimed if applications need it).
* **available:** The actual amount of memory available for starting new applications without swapping.

---

## 2. Using `htop` or `top` (Real-time & Process Details)
To see which processes are using the most memory in real-time.

### Option A: `htop` (Recommended, Visual)
If `htop` is not installed, install it via:
```bash
sudo apt install htop -y
```
Then run:
```bash
htop
```
*Press `F6` to sort processes by `MEM%` to see what is using the most RAM. Press `q` to exit.*

### Option B: `top` (Built-in)
If you don't have `htop` installed and want a built-in tool, run:
```bash
top
```
*Press `Shift+M` to sort the list by memory usage. Press `q` to exit.*

---

## 3. View Detailed Memory Information (`/proc/meminfo`)
To see the raw details of your system's memory:

```bash
cat /proc/meminfo
```
*This returns a long list of specific memory metrics (e.g., MemTotal, MemFree, Active, Inactive, etc.).*

---

## 4. Check Swap Space Usage
To see details about swap partitions or files:

```bash
swapon --show
```
