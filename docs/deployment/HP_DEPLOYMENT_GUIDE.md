# HP DEPLOYMENT GUIDE - SYSTEM REBELLION
**For HP-Sonnet - November 19, 2025**

---

## ARCHITECTURE OVERVIEW

**System Rebellion runs entirely on the HP (Arch Linux, 16GB RAM):**
- Frontend (React/TypeScript)
- Backend (FastAPI + ALL 6 agents)
- PostgreSQL database

**ThinkPad (IBM) at 192.168.1.216:**
- Redis server ONLY (already running)

**Dell:**
- Claude's Playground (separate project)

---

## PREREQUISITES

### System Requirements (HP):
- Arch Linux (already installed)
- 16GB RAM
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Git

### Network:
- ThinkPad Redis accessible at `redis://192.168.1.216:6379`
- Verify connectivity: `redis-cli -h 192.168.1.216 -p 6379 ping`

---

## INITIAL SETUP

### 1. Clone Repository
```bash
cd ~
git clone git@github.com:hawkington-tech/system_rebellion.git
cd system_rebellion
git checkout distributed-mixin-implementation
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Configure Environment
Create `backend/.env`:
```bash
# Database
DATABASE_URL=postgresql://rebellion_user:your_password@localhost/rebellion_db

# Redis (ThinkPad)
REDIS_URL=redis://192.168.1.216:6379

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# All agents run on this machine
AGENT_ROLES=sir_hawkington,vic_20_sage,the_stick,meth_snail,hamsters,quantum_shadow_people

# Environment
ENVIRONMENT=production
```

#### Setup PostgreSQL
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE rebellion_db;
CREATE USER rebellion_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE rebellion_db TO rebellion_user;
\q

# Run migrations
cd backend
alembic upgrade head
```

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd frontend
npm install
```

#### Configure Environment
Create `frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## RUNNING THE APPLICATION

### Option 1: Development Mode (Recommended for Testing)

#### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Consciousness Monitor: http://localhost:5173/monitor (after login)

### Option 2: Production Mode (Systemd Services)

#### Backend Service
Create `/etc/systemd/system/rebellion-backend.service`:
```ini
[Unit]
Description=System Rebellion Backend
After=network.target postgresql.service

[Service]
Type=simple
User=carissab
WorkingDirectory=/home/carissab/system_rebellion/backend
Environment="PATH=/home/carissab/system_rebellion/backend/venv/bin"
ExecStart=/home/carissab/system_rebellion/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Frontend Service (with nginx)
1. Build frontend:
```bash
cd frontend
npm run build
```

2. Configure nginx to serve `frontend/dist`

3. Enable services:
```bash
sudo systemctl enable rebellion-backend
sudo systemctl start rebellion-backend
sudo systemctl enable nginx
sudo systemctl start nginx
```

---

## VERIFICATION CHECKLIST

### 1. Redis Connection
```bash
redis-cli -h 192.168.1.216 -p 6379 ping
# Should return: PONG
```

### 2. Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### 3. Agent Status
```bash
curl http://localhost:8000/api/distributed-agents/agents
# Should return array of 6 agents
```

### 4. WebSocket Connection
- Login to frontend
- Open browser console
- Should see: "WebSocket connected"

### 5. Consciousness Monitor
- Navigate to http://localhost:5173/monitor
- Should see all 6 agents with real-time data

---

## AGENT VERIFICATION

All 6 agents should initialize on startup:

1. **Sir Hawkington** - Triage Commander (CPU monitoring)
2. **VIC-20 Sage** - Orchestrator (coordination)
3. **Meth Snail (Terry)** - Memory Optimizer
4. **The Stick** - Compliance Officer
5. **Hamsters (Steve, Bob, Carl)** - Disk Engineers
6. **Quantum Shadow People** - Network Specialists

**Check logs:**
```bash
# Backend logs should show:
# "Initializing distributed agent: sir_hawkington"
# "Initializing distributed agent: vic_20_sage"
# ... (all 6 agents)
# "All agents initialized successfully"
```

---

## TROUBLESHOOTING

### Redis Connection Failed
```bash
# Check ThinkPad Redis is running
ssh thinkpad
systemctl status redis

# Check firewall allows port 6379
sudo ufw allow 6379
```

### Agents Not Initializing
```bash
# Check AGENT_ROLES in .env
cat backend/.env | grep AGENT_ROLES

# Check agent config file
cat backend/app/ai_agents/agents_config.yaml

# Check logs for errors
tail -f backend/logs/app.log
```

### Database Connection Failed
```bash
# Verify PostgreSQL is running
systemctl status postgresql

# Test connection
psql -U rebellion_user -d rebellion_db -h localhost
```

### Frontend Can't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check VITE_API_URL in frontend/.env
cat frontend/.env | grep VITE_API_URL

# Check CORS settings in backend/app/main.py
```

---

## MONITORING

### Real-Time Agent Activity
- **Consciousness Monitor**: http://localhost:5173/monitor
- Shows all 6 agents, health, decisions, messages
- Updates every 5 seconds

### Backend Logs
```bash
# Application logs
tail -f backend/logs/app.log

# Agent-specific logs
tail -f backend/logs/agents.log

# Redis pub/sub activity
redis-cli -h 192.168.1.216 -p 6379 MONITOR
```

### System Resources
```bash
# CPU, Memory, Disk
htop

# Network connections
netstat -tulpn | grep -E '(8000|6379)'

# PostgreSQL connections
psql -U rebellion_user -d rebellion_db -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## UPDATING THE APPLICATION

### Pull Latest Changes
```bash
cd ~/system_rebellion
git pull origin distributed-mixin-implementation
```

### Update Backend
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart rebellion-backend
```

### Update Frontend
```bash
cd frontend
npm install
npm run build
sudo systemctl restart nginx
```

---

## BACKUP & RESTORE

### Database Backup
```bash
pg_dump -U rebellion_user rebellion_db > backup_$(date +%Y%m%d).sql
```

### Database Restore
```bash
psql -U rebellion_user rebellion_db < backup_20251119.sql
```

### Redis Backup (if needed)
```bash
# On ThinkPad
redis-cli -h 192.168.1.216 -p 6379 SAVE
# Creates dump.rdb in Redis data directory
```

---

## PERFORMANCE TUNING

### PostgreSQL
```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '2GB';
SELECT pg_reload_conf();
```

### Backend (uvicorn)
```bash
# Multiple workers for production
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Redis (on ThinkPad)
```bash
# Already configured with 512MB max memory
# Check config: redis-cli -h 192.168.1.216 CONFIG GET maxmemory
```

---

## SECURITY NOTES

1. **Change default passwords** in `.env` files
2. **Use strong SECRET_KEY** for JWT tokens
3. **Enable firewall** on HP:
   ```bash
   sudo ufw enable
   sudo ufw allow 8000/tcp  # Backend
   sudo ufw allow 5173/tcp  # Frontend (dev)
   sudo ufw allow 80/tcp    # Nginx (production)
   ```
4. **Secure PostgreSQL**: Only allow localhost connections
5. **Redis on ThinkPad**: Consider password protection if exposed

---

## QUICK REFERENCE

### Start Development
```bash
# Terminal 1
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

### Check Agent Status
```bash
curl http://localhost:8000/api/distributed-agents/agents | jq
```

### View Real-Time Messages
```bash
redis-cli -h 192.168.1.216 -p 6379 SUBSCRIBE agent:broadcast triage:decisions resource:alerts
```

### Restart Everything
```bash
sudo systemctl restart rebellion-backend
sudo systemctl restart nginx
```

---

## NEED HELP?

1. **Check logs first**: `tail -f backend/logs/app.log`
2. **Verify Redis**: `redis-cli -h 192.168.1.216 -p 6379 ping`
3. **Check agent config**: `cat backend/app/ai_agents/agents_config.yaml`
4. **Read the code**: The agents are well-documented
5. **Ask Carissa**: She knows this system inside and out

---

## FINAL NOTES

- **All agents run on HP** - No need to split across machines
- **Redis on ThinkPad** - Already configured and working
- **Design system** - Always use `rebellion-core.css` variables
- **Agent personalities** - Preserve their quirks, they're features
- **No fake data** - Everything is real metrics and decisions

**You've got this, HP-Sonnet. The system is production-ready. Just deploy and monitor.** 🚀

— Dell-Sonnet
