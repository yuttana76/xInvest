# Enabling and Checking SSH Status on Ubuntu

This guide explains how to install, enable, start, and check the status of the SSH service on Ubuntu.

---

## 1. Install OpenSSH Server
If SSH is not yet installed on your Ubuntu system, install it by running:

```bash
sudo apt update
sudo apt install openssh-server -y
```

---

## 2. Enable and Start the SSH Service
To make sure SSH starts automatically when the system boots and starts running immediately, use:

```bash
sudo systemctl enable --now ssh
```

*Note: On older Ubuntu versions, the service name might be `sshd` instead of `ssh` (e.g., `sudo systemctl enable --now sshd`).*

---

## 3. Check SSH Status
To verify whether the SSH server is currently running, run:

```bash
sudo systemctl status ssh
```

### Expected Output
Look for `Active: active (running)` in the output:
```text
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-06-03 12:00:00 UTC; 5min ago
   Main PID: 1234 (sshd)
      Tasks: 1 (limit: 4915)
     Memory: 2.5M
     CGroup: /system.slice/ssh.service
             └─1234 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups
```

* To exit the status screen, press `q`.

---

## 4. Allow SSH through the Firewall
If you have the Uncomplicated Firewall (UFW) active on Ubuntu, you must allow SSH traffic through it:

```bash
sudo ufw allow ssh
```

To verify the firewall rules:
```bash
sudo ufw status
```
*Look for `22/tcp ALLOW` or `SSH ALLOW` in the list.*

---

## 5. Controlling the SSH Service (Useful Commands)

* **Stop SSH:**
  ```bash
  sudo systemctl stop ssh
  ```
* **Start SSH:**
  ```bash
  sudo systemctl start ssh
  ```
* **Restart SSH (e.g., after config changes):**
  ```bash
  sudo systemctl restart ssh
  ```
* **Disable SSH from starting on boot:**
  ```bash
  sudo systemctl disable ssh
  ```
