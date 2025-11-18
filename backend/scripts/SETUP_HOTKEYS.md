# Hotkey Setup for System Rebellion

## XFCE Desktop (Dell) - Keyboard Shortcuts

### Step 1: Open Keyboard Settings

1. Open **Settings Manager** (Menu → Settings → Keyboard)
2. Go to **Application Shortcuts** tab
3. Click **Add** button

### Step 2: Add Wake Hotkey

**Command:**
```bash
xfce4-terminal --title="System Rebellion - Master Control" --command="/home/carissab/Documents/system_rebellion/backend/scripts/wake-the-misfits.sh" --hold
```

**Shortcut:** Press `Super+Shift+W` when prompted

**Description:** Wake the Rebellion (starts all services)

### Step 3: Add Shutdown Hotkey

**Command:**
```bash
xfce4-terminal --title="System Rebellion - Shutdown" --command="/home/carissab/Documents/system_rebellion/backend/scripts/shutdown-rebellion.sh" --hold
```

**Shortcut:** Press `Super+Shift+S` when prompted

**Description:** Shutdown the Rebellion (stops all services)

---

## Alternative: Manual Command Line Usage

### Wake the Rebellion
```bash
cd /home/carissab/Documents/system_rebellion/backend/scripts
./wake-the-misfits.sh
```

### Shutdown the Rebellion
```bash
cd /home/carissab/Documents/system_rebellion/backend/scripts
./shutdown-rebellion.sh
```

---

## What Each Hotkey Does

### Super+Shift+W (Wake)
1. ✅ Connects to IBM ThinkPad → Starts Redis
2. ✅ Connects to HP → Starts Backend (uvicorn)
3. ✅ Starts Frontend locally (vite)
4. ✅ Monitors all services
5. ✅ Auto-restarts if any service crashes
6. ✅ Shows beautiful status dashboard

### Super+Shift+S (Shutdown)
1. ✅ Stops Frontend on Dell
2. ✅ Stops Backend on HP
3. ✅ Stops Redis on IBM ThinkPad
4. ✅ Cleans up all log files
5. ✅ Removes PID files
6. ✅ Shows shutdown confirmation

---

## Troubleshooting

### If hotkeys don't work:

1. **Check script permissions:**
   ```bash
   ls -la /home/carissab/Documents/system_rebellion/backend/scripts/*.sh
   ```
   All should have `x` (executable) permission.

2. **Test scripts manually:**
   ```bash
   cd /home/carissab/Documents/system_rebellion/backend/scripts
   ./wake-the-misfits.sh
   ```

3. **Check SSH connections:**
   ```bash
   ssh carissa@192.168.1.216 "echo 'IBM OK'"
   ssh carissa@192.168.1.199 "echo 'HP OK'"
   ```

4. **View logs:**
   ```bash
   tail -f /home/carissab/Documents/system_rebellion/backend/logs/*.log
   ```

---

## Service URLs After Wake

- **Frontend:** http://localhost:5173
- **Backend:** http://192.168.1.199:8000
- **API Docs:** http://192.168.1.199:8000/docs
- **Redis:** redis://192.168.1.216:6379

---

## Advanced: i3 Window Manager (HP)

If you want hotkeys on the HP as well, add to `~/.config/i3/config`:

```
# System Rebellion Hotkeys
bindsym $mod+Shift+w exec --no-startup-id xfce4-terminal --command="/home/carissa/Documents/system_rebellion/backend/scripts/wake-the-misfits.sh"
bindsym $mod+Shift+s exec --no-startup-id xfce4-terminal --command="/home/carissa/Documents/system_rebellion/backend/scripts/shutdown-rebellion.sh"
```

Then reload i3: `$mod+Shift+r`

---

## Notes

- **Logs are cleaned on shutdown** to save space on IBM ThinkPad (70GB storage)
- **Auto-restart enabled** - services will restart if they crash
- **Monitoring runs continuously** - Press Ctrl+C to stop monitoring (services keep running)
- **Safe to run multiple times** - Scripts clean up old processes first

---

## Quick Reference

| Hotkey | Action | What It Does |
|--------|--------|--------------|
| `Super+Shift+W` | Wake | Start all services with monitoring |
| `Super+Shift+S` | Shutdown | Stop all services and clean logs |

**Super** = Windows key / Command key
