# Troubleshooting Wake Scripts

## Issue: SSH Asks for Password

**Symptom:**
```
carissa@192.168.1.216's password:
```

**Cause:** Passwordless SSH is not set up

**Fix:**
```bash
cd /home/carissab/Documents/system_rebellion/backend/scripts
./setup-ssh-keys.sh
```

This will:
1. Generate SSH key if needed
2. Copy key to IBM ThinkPad
3. Copy key to HP
4. Test both connections

You'll need to enter passwords **once** during setup, then never again!

---

## Issue: Redis Fails to Start

**Symptom:**
```
❌ Redis - Failed to start Redis
```

**Check the log:**
```bash
cat /home/carissab/Documents/system_rebellion/backend/logs/redis.log
```

**Common causes:**

### 1. Redis not installed on IBM
```bash
ssh carissa@192.168.1.216 "redis-server --version"
```

If not installed:
```bash
ssh carissa@192.168.1.216
sudo apt-get update
sudo apt-get install redis-server
```

### 2. Redis already running
```bash
ssh carissa@192.168.1.216 "redis-cli ping"
```

If it responds "PONG", Redis is already running! You're good to go.

### 3. Permission issues
The script now runs Redis without sudo. If you need sudo, you'll need to configure passwordless sudo:

```bash
ssh carissa@192.168.1.216
sudo visudo
# Add this line:
carissa ALL=(ALL) NOPASSWD: /usr/bin/systemctl start redis-server
carissa ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop redis-server
carissa ALL=(ALL) NOPASSWD: /usr/bin/pkill redis-server
```

---

## Issue: Backend Fails to Start

**Check the log:**
```bash
cat /home/carissab/Documents/system_rebellion/backend/logs/backend.log
```

**Common causes:**

### 1. Project not on HP
```bash
ssh carissa@192.168.1.199 "ls -la /home/carissa/Documents/system_rebellion/backend"
```

If not found, you need to clone the repo on HP:
```bash
ssh carissa@192.168.1.199
cd /home/carissa/Documents
git clone <your-repo-url> system_rebellion
```

### 2. Venv not set up
```bash
ssh carissa@192.168.1.199 "ls -la /home/carissa/Documents/system_rebellion/backend/venv"
```

If not found:
```bash
ssh carissa@192.168.1.199
cd /home/carissa/Documents/system_rebellion/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Port 8000 already in use
```bash
ssh carissa@192.168.1.199 "lsof -i :8000"
```

Kill the process:
```bash
ssh carissa@192.168.1.199 "pkill -f uvicorn"
```

---

## Issue: Frontend Fails to Start

**Check the log:**
```bash
cat /home/carissab/Documents/system_rebellion/backend/logs/frontend.log
```

**Common causes:**

### 1. node_modules missing
```bash
cd /home/carissab/Documents/system_rebellion/frontend
npm install
```

### 2. Port 5173 already in use
```bash
lsof -i :5173
```

Kill the process:
```bash
pkill -f vite
```

### 3. Node/npm not installed
```bash
node --version
npm --version
```

If not installed:
```bash
# Install nvm first
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts
```

---

## Quick Diagnostics

### Test all SSH connections
```bash
echo "Testing IBM..."
ssh -o BatchMode=yes carissa@192.168.1.216 "echo 'IBM OK'" && echo "✅ IBM" || echo "❌ IBM"

echo "Testing HP..."
ssh -o BatchMode=yes carissa@192.168.1.199 "echo 'HP OK'" && echo "✅ HP" || echo "❌ HP"
```

### Test Redis manually
```bash
ssh carissa@192.168.1.216 "redis-cli ping"
```

Should respond: `PONG`

### Test Backend manually
```bash
curl http://192.168.1.199:8000/health
```

Should respond with JSON

### Test Frontend manually
```bash
curl http://localhost:5173
```

Should respond with HTML

---

## Manual Service Start

If the scripts fail, start services manually:

### Start Redis on IBM
```bash
ssh carissa@192.168.1.216
redis-server --daemonize yes
redis-cli ping  # Should respond PONG
```

### Start Backend on HP
```bash
ssh carissa@192.168.1.199
cd /home/carissa/Documents/system_rebellion/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend on Dell
```bash
cd /home/carissab/Documents/system_rebellion/frontend
npm run dev
```

---

## Still Having Issues?

### Check all prerequisites:

**IBM ThinkPad:**
- [ ] Redis installed: `redis-server --version`
- [ ] SSH key accepted: `ssh -o BatchMode=yes carissa@192.168.1.216 "echo OK"`

**HP:**
- [ ] Project cloned: `ssh carissa@192.168.1.199 "ls /home/carissa/Documents/system_rebellion"`
- [ ] Venv exists: `ssh carissa@192.168.1.199 "ls /home/carissa/Documents/system_rebellion/backend/venv"`
- [ ] SSH key accepted: `ssh -o BatchMode=yes carissa@192.168.1.199 "echo OK"`

**Dell:**
- [ ] Node installed: `node --version`
- [ ] npm installed: `npm --version`
- [ ] node_modules exists: `ls frontend/node_modules`

---

## Get Help

If you're still stuck, gather this info:

```bash
# System info
uname -a
echo "Dell IP: $(hostname -I)"

# SSH test
ssh -v carissa@192.168.1.216 "echo test" 2>&1 | grep -i "auth"

# Redis test
ssh carissa@192.168.1.216 "redis-cli ping" 2>&1

# Backend test
ssh carissa@192.168.1.199 "cd /home/carissa/Documents/system_rebellion/backend && ls -la" 2>&1

# Logs
cat /home/carissab/Documents/system_rebellion/backend/logs/*.log
```

Share this output for debugging!
