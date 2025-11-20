# Agent Theater Navigation Guide

## 🎭 NEW Agent Theater (LiveAgentTheater)
**URL:** `/dashboard/agent-theater` or `/agent-theater` (redirects)

**Features:**
- Modern, animated agent personality cards
- Live agent activity with personality-based descriptions
- Framer Motion animations
- 60-second update intervals
- WebSocket-based real-time data
- Beautiful gradient cards with agent personalities

**Files:**
- Component: `frontend/src/components/agent-theater/LiveAgentTheater.tsx`
- Card: `frontend/src/components/agent-theater/LiveAgentCard.tsx`
- Page: `frontend/src/pages/LiveAgentTheaterPage.tsx`

**Visual Indicator:** Title shows "🎭 Agent Theater NEW"

---

## ⚠️ OLD Agent Theater (AgentTheaterEnhanced)
**URL:** `/dashboard/agent-theater-old`

**Features:**
- Introspection view with AST method tracking
- Theater view with traditional agent cards
- Toggle between two modes
- Redux-based state management
- Connection status indicators

**Files:**
- Component: `frontend/src/components/agent-theater/AgentTheater.tsx`

**Visual Indicator:** Title shows "Agent Theater OLD VERSION"

---

## How to Check Which One You're On

1. **Check the URL in your browser:**
   - `/dashboard/agent-theater` = NEW ✅
   - `/dashboard/agent-theater-old` = OLD ⚠️

2. **Check the browser console:**
   - NEW: `🎭 LiveAgentTheaterPage mounted - YOU ARE ON THE NEW THEATER!`
   - OLD: `⚠️ OLD AgentTheaterEnhanced mounted - You are on the OLD theater!`

3. **Check the page title:**
   - NEW: Has a green "NEW" badge
   - OLD: Has an orange "OLD VERSION" badge

---

## Navigation

### From MainLayout Sidebar:
Click "Agent Theater" → Goes to NEW theater (`/dashboard/agent-theater`)

### From MainNavigation:
Click "Agent Theater" link → Goes to NEW theater (via redirect)

### To Access OLD Theater:
Manually navigate to `/dashboard/agent-theater-old`

---

## Troubleshooting

If you're seeing the old theater when you expect the new one:

1. **Clear browser cache** (Ctrl+Shift+R or Cmd+Shift+R)
2. **Check the URL** - Make sure you're at `/dashboard/agent-theater` not `/dashboard/agent-theater-old`
3. **Check console logs** - Look for the mount messages
4. **Hard refresh** - Close all tabs and reopen
5. **Check routing** - Verify `App.tsx` line 159 points to `LiveAgentTheaterPage`

---

## Default Routes

After login/onboarding, you are redirected to `/agent-theater` which automatically redirects to `/dashboard/agent-theater` (the NEW theater).
