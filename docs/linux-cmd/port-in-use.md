# Troubleshooting "Address Already in Use" (Port Conflicts) on Linux/Ubuntu

When running `docker compose` or starting web servers, you might encounter the following error:

```text
failed to bind host port 0.0.0.0:3001/tcp: address already in use
```

This means another process on your Ubuntu machine is already listening on port `3001`.

---

## Step 1: Find what process is using the port

Run either of the following commands to identify the process ID (PID) using the port:

### Option A: Using `lsof` (Recommended)
```bash
sudo lsof -i :3001
```
*Expected output:*
```text
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node    98765 bom    23u  IPv4  82713      0t0  TCP *:3001 (LISTEN)
```
In this example, the **PID** is `98765`.

### Option B: Using `netstat`
```bash
sudo netstat -nlp | grep 3001
```

---

## Step 2: Stop or Kill the process

Once you have the PID, you can stop the process:

### 1. Gracefully terminate the process
```bash
sudo kill 98765
```
*(Replace `98765` with the actual PID from Step 1).*

### 2. Forcefully kill the process (if it doesn't stop)
```bash
sudo kill -9 98765
```

---

## Step 3: Alternative Solutions

### Option A: Check for orphan Docker containers
Sometimes Docker containers from a previous project run are still using the port. Run:
```bash
docker ps
```
If you see a container using port `3001`, stop it:
```bash
docker stop <container_name_or_id>
```

### Option B: Change the port in `docker-compose.dev.yml`
If you want to keep the other process running, you can change the port mapping in your `docker-compose.dev.yml` under the `frontend` service:

```yaml
  frontend:
    ports:
      - "3002:3000"  # Change the host port from 3001 to 3002
```
Now the frontend will be accessible at `http://your_ubuntu_ip:3002`.
