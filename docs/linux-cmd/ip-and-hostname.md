# Checking Ubuntu IP Address and Managing Hostnames (Preventing IP Changes)

To connect to Ubuntu via SSH, you need to know its IP address or Hostname. Because IP addresses on local networks can change when the system restarts or reconnects (dynamic IP), using a **Hostname** or configuring a **Static IP** is recommended.

---

## Part 1: How to find the Ubuntu IP Address
Run any of the following commands in the Ubuntu terminal to see its current local IP address:

### Option A: Clean IP List (Recommended)
```bash
hostname -I
```
*This returns a list of active IP addresses (e.g., `192.168.1.50`).*

### Option B: Detailed Network Interfaces
```bash
ip a
```
*Look for `inet` under your network interface (like `eth0` or `wlan0`).*

---

## Part 2: How to Connect via Hostname (No IP Required)
To avoid typing the IP address (especially if it changes), you can use the Ubuntu machine's **Hostname**.

1. **Find the hostname on the Ubuntu machine:**
   ```bash
   hostname
   ```
   *(For example, if it returns: `my-ubuntu-server`)*

2. **Connect from your Mac using `.local`:**
   ```bash
   ssh newusername@my-ubuntu-server.local
   ```
   *Ubuntu uses `avahi-daemon` (mDNS) by default, which broadcasts its hostname on the local network. Your Mac will automatically resolve `my-ubuntu-server.local` to the correct IP address even if the IP changes.*

---

## Part 3: How to Prevent the IP Address from Changing
If you prefer using the IP address but want to keep it permanent, you have two options:

### Option A: DHCP IP Reservation on your Router (Recommended)
This is the easiest and most stable method. It guarantees the IP never changes, without modifying Ubuntu's system files.
1. Log in to your Wi-Fi Router's admin panel (e.g., `192.168.1.1`).
2. Find the **DHCP Server / IP Reservation / Static IP** setting.
3. Find your Ubuntu device in the list (using its MAC Address or Hostname).
4. Reserve a specific IP (e.g., `192.168.1.100`) for that MAC Address.
5. Save changes. The router will now always assign this IP to your Ubuntu server.

### Option B: Configure a Static IP directly in Ubuntu (Netplan)
If you want to configure it directly on the server, Ubuntu uses **Netplan**:

1. Find your network interface name (e.g., `enp3s0` or `eth0`):
   ```bash
   ip link
   ```
2. Open the Netplan configuration file (usually in `/etc/netplan/`):
   ```bash
   sudo nano /etc/netplan/01-netcfg.yaml
   ```
   *(Note: The filename might vary, use `ls /etc/netplan` to verify).*
3. Modify/create the configuration to look like this (substitute with your interface name, desired IP, gateway, and DNS):
   ```yaml
   network:
     version: 2
     renderer: networkd
     ethernets:
       enp3s0:
         dhcp4: no
         addresses:
           - 192.168.1.100/24
         nameservers:
           addresses: [8.8.8.8, 1.1.1.1]
         routes:
           - to: default
             via: 192.168.1.1
   ```
4. Test and apply the settings:
   ```bash
   sudo netplan try
   sudo netplan apply
   ```

---

## Part 4: Create a Shortcut on your Mac (SSH Config)
On your Mac, you can create a shortcut so you only need to type `ssh ubuntu`:

1. Open/create your SSH config file on your Mac:
   ```bash
   nano ~/.ssh/config
   ```
2. Add the following block:
   ```text
   Host ubuntu
       HostName my-ubuntu-server.local
       User newusername
   ```
3. Save and close. Now you can connect simply by running:
   ```bash
   ssh ubuntu
   ```
