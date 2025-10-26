# Agent Theater Routing Test

## Quick Test Steps

1. **Start the frontend dev server** (if not already running):
   ```bash
   cd frontend
   npm run dev
   ```

2. **Open browser console** (F12 or Cmd+Option+I)

3. **Navigate to Agent Theater:**
   - Click "Agent Theater" in the sidebar
   - OR go to: `http://localhost:5173/dashboard/agent-theater`

4. **Check console output:**
   - ✅ Should see: `🎭 LiveAgentTheaterPage mounted - YOU ARE ON THE NEW THEATER!`
   - ❌ Should NOT see: `⚠️ OLD AgentTheaterEnhanced mounted`

5. **Check page title:**
   - ✅ Should see: "🎭 Agent Theater NEW" with green badge
   - ❌ Should NOT see: "OLD VERSION" badge

6. **Check URL:**
   - ✅ Should be: `/dashboard/agent-theater`
   - ❌ Should NOT be: `/dashboard/agent-theater-old`

---

## If You See the OLD Theater

### Scenario 1: URL is `/dashboard/agent-theater-old`
**Solution:** Navigate to `/dashboard/agent-theater` instead

### Scenario 2: URL is correct but showing old theater
**Solution:** 
1. Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Close all tabs and reopen
4. Check if there's a build error in the terminal

### Scenario 3: Console shows OLD component mounting
**Solution:**
1. Check `App.tsx` line 159 - should be `<LiveAgentTheaterPage />`
2. Restart the dev server
3. Clear browser cache

---

## Component Hierarchy

```
App.tsx
  └─ MainLayout (at /dashboard/*)
      └─ Route: /dashboard/agent-theater
          └─ LiveAgentTheaterPage
              └─ LiveAgentTheater
                  └─ LiveAgentCard (x6 agents)
```

---

## Files Modified

1. `App.tsx` - Renamed import to `AgentTheaterOld`
2. `LiveAgentTheaterPage.tsx` - Added debug console.log
3. `AgentTheater.tsx` - Added debug console.log and "OLD VERSION" badge
4. `LiveAgentTheater.tsx` - Added "NEW" badge to title

---

## Rollback Instructions

If you want to revert to the old theater as default:

1. Edit `App.tsx` line 159:
   ```tsx
   <Route path="agent-theater" element={<AgentTheaterOld />} />
   ```

2. Edit line 160:
   ```tsx
   <Route path="agent-theater-new" element={<LiveAgentTheaterPage />} />
   ```
