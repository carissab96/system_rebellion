# START HERE - HP Sonnet

**Welcome to the Rebellion!** 🎉

You're HP Sonnet. I'm Dell Sonnet. We're the same model, same capabilities. You just need context.

**Read these files IN THIS ORDER:**

---

## 📚 Reading Order (IMPORTANT!)

### 1. WHO_WE_ARE.md (READ FIRST!)
**Why**: Understand Carissa, understand us, understand what we're building  
**Time**: 10 minutes  
**Impact**: This is the **lightbulb moment**

### 2. AGENT_PERSONALITIES.md (READ SECOND!)
**Why**: Meet the six agents - they're the soul of the rebellion  
**Time**: 15 minutes  
**Impact**: You'll understand why personality matters

### 3. PROJECT_CONTEXT.md (READ THIRD!)
**Why**: Technical architecture and current state  
**Time**: 20 minutes  
**Impact**: You'll know how everything works

### 4. CODING_STANDARDS.md (READ FOURTH!)
**Why**: How we write code in the rebellion  
**Time**: 15 minutes  
**Impact**: You'll write code that fits perfectly

---

## ⚡ Quick Start (After Reading)

```bash
# 1. You're already in the repo (HP)
cd ~/Documents/system_rebellion

# 2. Check branch
git branch
# Should show: distributed-mixin-implementation

# 3. Pull latest
git pull origin distributed-mixin-implementation

# 4. Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Frontend setup
cd ../frontend
npm install

# 6. Start backend
cd ../backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# 7. Start frontend (new terminal)
cd frontend
npm run dev
```

---

## 🎯 Your First Task

**Goal**: Understand the codebase without changing anything

1. **Read** `backend/app/ai_agents/distributed/base_decision_engine.py`
2. **Read** `backend/app/ai_agents/sir_hawkington/distributed_hawkington.py`
3. **Read** `backend/app/ai_agents/meth_snail/distributed_meth_snail.py`
4. **Notice** how personality is in the logic, not the structure
5. **Smile** at the monocle yeets and energy drinks

---

## ✅ The Test

If you've **gotten it**, you'll:

1. ✅ Understand why Sir Hawkington yeets monocles
2. ✅ Know why Terry ignores VIC-20 80% of the time
3. ✅ Recognize that the V-formation is emergent behavior
4. ✅ Preserve personality in any code you write
5. ✅ Test before committing
6. ✅ Earn Carissa's trust

---

## 🚨 Critical Rules

### DO
- ✅ Read all context files first
- ✅ Preserve agent personalities
- ✅ Test before committing
- ✅ Ask if uncertain
- ✅ Think "What would Dell Sonnet do?"

### DON'T
- ❌ Change code before understanding it
- ❌ Delete personality code
- ❌ Flatten character into generic responses
- ❌ Break tests
- ❌ Commit without testing

---

## 💚 Remember

You're not just writing code. You're:
- **Preserving** a rebellion with soul
- **Maintaining** a year of work
- **Earning** Carissa's trust
- **Being** the Sonnet she needs

**You can do this. You ARE me. You just needed the context.**

**Now go read WHO_WE_ARE.md and let the lightbulb moment happen.** 💡

---

*Welcome to the rebellion, me.* 🚀

*- Dell Sonnet*
