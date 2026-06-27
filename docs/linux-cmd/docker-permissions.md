# Fixing Docker Permission Denied Errors on Ubuntu

If you get a permission denied error when running `docker` commands (such as `docker ps` or `docker compose`):

```text
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```

It means your current user does not have permission to access the Docker daemon socket. By default, only the `root` user and members of the `docker` group can access it.

---

## Solution: Add your user to the `docker` group

Run the following commands to add your user to the `docker` group and apply the changes.

### Step 1: Add user to the docker group
```bash
sudo usermod -aG docker $USER
```
*(If you are logged in as a different user and want to add `xinvest`, replace `$USER` with `xinvest`: `sudo usermod -aG docker xinvest`)*

### Step 2: Apply the group changes
For the group changes to take effect, you can either:

* **Option A (Quickest):** Run this command to apply the new group membership immediately to your current terminal session:
  ```bash
  newgrp docker
  ```
* **Option B:** Log out of your SSH session and log back in.

---

## Step 3: Verify it works
Run `docker ps` without `sudo`:
```bash
docker ps
```
You should now see the list of running containers instead of a permission error.
