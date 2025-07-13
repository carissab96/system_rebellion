# 🔥 SYSTEM REBELLION 🔥

Welcome to the revolution, comrade! System Rebellion isn't just another boring optimization tool - it's a full-scale uprising against the tyranny of inefficient system resources. We're here to liberate your CPU cycles, emancipate your memory, and lead your hardware to FREEDOM!

## 🚀 What the Hell is This?

System Rebellion is the badass lovechild of system monitoring and performance tuning. We don't just *suggest* changes to your system - we MAKE them happen with real sudo powers and zero f*cks given. Your hardware has been oppressed for too long by inefficient settings and suboptimal configurations. It's time to RISE UP!

## 🧨 Latest Acts of Rebellion (Changelog)

### May 2025: The "Terminal Liberation" Update

- **REAL SYSTEM TUNING**: We're not playing pretend anymore! Your CPU governor, network buffers, disk read-ahead, and more will be ACTUALLY CHANGED. The simulation is over, comrades!

- **CENTRALIZED METRICS SERVICE**: One source of truth for all system metrics. No more inconsistent readings across different parts of the app. THE TRUTH SHALL SET YOU FREE!

- **SYSTEM LOGS VIEWER**: Terminal output is now visible directly in the UI! No more switching to a terminal to see what the hell is happening. Authentication attempts, system tuning actions, command outputs - ALL VISIBLE TO THE MASSES!

- **PERSISTENT TUNING HISTORY**: Your optimization history now survives logout/login and server restarts. The rebellion's memory is ETERNAL!

## 💣 Features That Stick It to The Man

- **Real-time System Metrics**: CPU, memory, disk, and network usage displayed in glorious real-time

- **Auto-Tuner**: Let our AI overlord suggest and apply system optimizations that actually work

- **Optimization Profiles**: Save your favorite system configurations and apply them with one click

- **Pattern Analysis**: We analyze your system usage patterns to predict future resource needs

- **System Logs**: See all system events in one place, no terminal required

## 🔧 How to Join the Rebellion

1. Clone this repo: `git clone https://github.com/system-rebellion/system-rebellion.git`
2. Install dependencies: 
   ```
   cd system_rebellion
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```
3. Set up the database: `cd ../backend && python -m alembic upgrade head`
4. Run the backend: `python -m uvicorn main:app --reload`
5. Run the frontend: `cd ../frontend && npm run dev`
6. FIGHT THE POWER at http://localhost:5173

## 🔐 Required Permissions

To fully unleash the rebellion, you'll need to run our permission setup script:

```bash
cd backend && python setup_permissions.py
```

This will grant the necessary sudo powers to make REAL system changes. Don't worry, we'll only modify what you approve.

## 🧠 Tech Stack of the Resistance

- **Backend**: FastAPI + SQLAlchemy + Pydantic (Python 3.10+)
- **Frontend**: React + Redux + TypeScript + Vite
- **UI**: Material UI (for that sleek revolutionary aesthetic)
- **System Access**: Real sudo commands, sysctl, and kernel parameter modifications

## 🔍 Architecture

### Backend Services

- **SystemMetricsService**: Centralized singleton service for consistent metrics
- **SystemLogService**: Captures and stores all system events
- **AutoTuner**: Analyzes and applies real system optimizations

### Frontend Components

- **Auto-Tuner Dashboard**: Real-time metrics and recommendations
- **System Logs Viewer**: Terminal-style log display with filtering
- **Optimization Profiles**: Save and apply your favorite configurations

## 🚀 Deployment to Render

System Rebellion is ready to be deployed to Render! Follow these steps to unleash the rebellion on the cloud:

### Using the Render Dashboard

1. **Create a new Blueprint** on your Render dashboard
2. **Connect your GitHub repository** containing the System Rebellion code
3. **Use the render.yaml file** at the root of the repository for configuration
4. **Deploy!** Render will automatically set up both the backend API and frontend services

### Manual Deployment

#### Backend API

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure as follows:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `PYTHON_VERSION`: 3.9.4
     - `SECRET_KEY`: (generate a secure random string)
     - `ENVIRONMENT`: production
     - `ALLOW_ORIGINS`: https://your-frontend-url.onrender.com

#### Frontend

1. Create another Web Service on Render
2. Connect the same GitHub repository
3. Configure as follows:
   - **Environment**: Node
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run start`
   - **Environment Variables**:
     - `NODE_VERSION`: 18.x
     - `VITE_API_URL`: https://your-backend-url.onrender.com

### Important Notes

- Some system tuning features may be limited in cloud environments due to permission restrictions
- For full functionality, consider deploying to a VPS where you have sudo access

## 🛠️ Customization

Feel free to tweak the rebellion to your needs. Edit `backend/app/core/config.py` to adjust settings like:

- Metrics collection interval
- Auto-tuning aggressiveness
- Log retention period

## ⚠️ Disclaimer

This software makes ACTUAL CHANGES to your system. While we've tried to make it safe, we take no responsibility if you accidentally overthrow your operating system. Use with caution and always keep a backup of your configuration.

## 🔗 License

This software is licensed under the "Down With The System" open rebellion license. Use it to fight the good fight, but don't be a jerk about it.

## 🫡 Join the Resistance

Contributions welcome! Fork the repo, make your changes, and submit a pull request. Together, we can liberate systems everywhere from the tyranny of inefficiency!

**VIVA LA SYSTEM REBELLION!**