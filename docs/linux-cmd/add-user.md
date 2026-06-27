# ssh
>ssh xinvest@192.168.1.42

# Creating a New User and Configuring SSH Access on Ubuntu

This guide explains how to create a new user on Ubuntu and configure it for secure SSH access.

---

## Step 1: Create the New User

Log in to your Ubuntu server using an account with `sudo` access, and run the following command:

```bash
sudo adduser newusername
```
*Replace `newusername` with your desired username.*
(xinvest/Password)

* You will be prompted to set and confirm a password for the new user.
* You can fill in the optional details (Full Name, Room Number, etc.) or simply press **Enter** to skip them.

---

## Step 2: Grant Administrator (Sudo) Privileges (Optional)

If the new user needs administrator privileges (the ability to run commands with `sudo`), add them to the `sudo` group:

```bash
sudo usermod -aG sudo newusername
```

---

## Step 3: Configure SSH Access

There are two ways to allow the new user to connect via SSH: **SSH Key-based Authentication** (secure, recommended) or **Password Authentication** (simpler, less secure).

### Method A: SSH Key Authentication (Recommended & Secure)

Instead of using passwords, this method uses cryptographic keys to authenticate the connection.

1. **On your local Mac/PC:** Check if you already have an SSH key pair. Open your terminal and run:
   ```bash
   cat ~/.ssh/id_rsa.pub
   ```
   If you see a long string starting with `ssh-rsa` or `ssh-ed25519`, copy it.
   
   *(If you don't have one, generate a key pair first by running `ssh-keygen -t rsa -b 4096` and pressing Enter through the prompts).*

2. **On the Ubuntu server:** Switch to the new user:
   ```bash
   su - newusername
   ```

3. **Create the SSH directory and authorized keys file:**
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   touch ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

4. **Add your public key:** Open the `authorized_keys` file:
   ```bash
   nano ~/.ssh/authorized_keys
   ```
   Paste the public key you copied from your Mac/PC, then save and exit (press `Ctrl+O`, `Enter`, and then `Ctrl+X`).

5. **Test the connection from your local Mac/PC:**
   ```bash
   ssh newusername@your_ubuntu_ip
   ```

---

### Method B: Password Authentication (Simpler but Less Secure)

By default, Ubuntu allows password authentication. If it is disabled, you can enable it:

1. **On the Ubuntu server:** Open the SSH configuration file:
   ```bash
   sudo nano /etc/ssh/sshd_config
   ```

2. Find the line `PasswordAuthentication` and make sure it is set to `yes`:
   ```text
   PasswordAuthentication yes
   ```
   *(If it has a `#` at the beginning, delete the `#` to uncomment it).*

3. Save the file and restart the SSH service to apply changes:
   ```bash
   sudo systemctl restart ssh
   ```

4. **Test the connection from your local Mac/PC:**
   ```bash
   ssh newusername@your_ubuntu_ip
   ```
   - local land:192.168.10.1
   - wirless:192.168.1.42
   *Enter the password you created in Step 1 when prompted.*

---

## Resetting / Changing a User's Password

If you have admin/sudo access on the Ubuntu machine (either physically or logged in under a different admin user), you can reset any user's password.

### Option A: Reset another user's password (requires sudo)
Run this command from an admin account:
```bash
sudo passwd username
```
*(For example, to reset `xinvest`'s password: `sudo passwd xinvest`)*

1. Type the new password when prompted.
2. Retype the new password to confirm.
*(Note: No characters will show on the screen while typing).*

### Option B: Change your own password
If you are already logged in as that user:
```bash
passwd
```
1. Enter your **current** password.
2. Enter and confirm your **new** password.

