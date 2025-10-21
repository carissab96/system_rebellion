# dev.to draft (longform)

---
Title: A night in the life of Hawkington’s agents (and what it *actually* means)
Published: false
Tags: devops, observability, automation, ai, architecture
Cover_image: <add-your-image-url>
Canonical_url: <optional>
---

## TL;DR
We built a small ensemble of autonomous assistants—The Stick (policy), Hamsters (infra hygiene), Quantum Shadow People (prediction), and VIC‑20 Sage (coordination)—that log every action to a central memory bank (UTC + JSON). This post mixes a short story with real event shapes and explains how the system stays inside guardrails.

## Why a story?
Because the night shift is a vibe. But under the vibe are typed events, thresholds, and small, safe changes. We’ll alternate narrative → translation.

## Narrative → Translation

**Narrative**
> Midnight rolls into 03:07. A squeak—not panic, just “heads up.” The central memory bank writes it down. The Stick clicks audit; Hamsters free space; QSP predicts a spike; VIC‑20 Sage drafts a plan that degrades like silk, not sandpaper.

**What this really means**
- An anomaly crosses a policy threshold.
- We write a UTC‑timestamped event with a typed `event_type` and `details`.
- Prediction models flag likely next failures; coordinator chooses a low‑risk sequence and a rollback plan.

**Example event**
```json
{
  "event_type": "qsp.prewarm_triggered",
  "agent_name": "quantum_shadow_people",
  "occurred_at": "2025-09-02T03:07:11Z",
  "confidence": 0.88,
  "details": {
    "reason": "latency_spike_predicted",
    "forecast_horizon_min": 7,
    "relevant_agents": ["hamsters", "vic20_sage"],
    "guardrail": "no_user_impact"
  }
}
```

**Narrative**
> We don’t YOLO‑fix in the dark. Every action checks a budget. If a step exceeds it, the plan pauses and escalates with a readable summary.

**Translation**
- Decisions are data structures, not vibes: `confidence`, `estimated_duration`, `tags`, `reason`.
- Every step validates guardrails (resource caps, time windows, freeze calendars) and is explainable later.

**Decision shape**
```json
{
  "type": "vic20.plan_step",
  "confidence": 0.91,
  "estimated_duration_sec": 180,
  "reason": "qsp.predicted_spike AND hamsters.space_ok",
  "tags": ["prewarm","low_risk"],
  "rollback": {"enabled": true, "max_duration_sec": 30}
}
```

**Narrative**
> Meth Snail shows up when slow is fast—proposes a single perfect diff: replace guess with measurement. The Hawk nods; we merge during quiet minutes.

**Translation**
- Human‑in‑the‑loop: stage → diff → low‑blast deploy. Before/after logged as `fix_applied` with a link.

**Shift close**
```json
{
  "event_type": "vic20.harmony_snapshot",
  "agent_name": "vic20_sage",
  "occurred_at": "2025-09-02T06:12:41Z",
  "details": {"status": "harmony_maintained", "changes": 3, "rollbacks": 0, "learning_interactions": 2, "success_rate": 1.0}
}
```

## Architecture sketch
- **central_memory_bank**: append‑only log with `(agent_name, event_type, occurred_at, details)`.
- **learning tables**: `agent_learning_interactions`, `user_learning_patterns`, `agent_global_patterns` for provenance and fast reads.
- **coordinator**: chooses the smallest safe change first; progressive rollout + auto‑rollback.
- **guardrails**: policy engine (The Stick) blocks or escalates out‑of‑budget actions.

## Principles
- Zero fake data. UTC everywhere. JSON all the way down.
- Decisions must be explainable and reversible.
- Prefer 100 small wins to 1 big rescue.

## What we’re opening up
- Event taxonomy + schemas
- Minimal SDK to emit/query events
- Sample dashboards & rollup jobs

## What’s coming next
- Public demos + early‑adopter program
- UI/UX: timeline, agent cards, harmony snapshots

**Want to kick the tires or help shape it?**
- Join the GitHub discussion (link below)
- Tell us what would make this useful on day one

---

# Reddit post (trimmed, conversational)

**Title**: We built a tiny ensemble of agents that keep prod calm at 3AM (story + real event shapes)

**TL;DR**: Agents log everything to a central memory bank (UTC + JSON). QSP predicts spikes, Hamsters do hygiene, The Stick sets guardrails, VIC‑20 coordinates rollouts. No YOLO fixes, everything has a budget & rollback. Looking for feedback, not customers.

**Story bite**
> Midnight → 03:07. A squeak, not panic. The memory bank writes it down. The Stick audits; Hamsters free space; QSP pre‑warms; VIC‑20 rolls out silk‑smooth changes.

**What this actually means**
- Typed events + UTC timestamps
- Prediction → small safe changes → rollback if budget breached

**Example event**
```json
{"event_type":"qsp.prewarm_triggered","agent_name":"quantum_shadow_people","occurred_at":"2025-09-02T03:07:11Z","confidence":0.88,"details":{"forecast_horizon_min":7,"guardrail":"no_user_impact"}}
```

**Ask**
- If you run SRE/DevOps: what would make this useful on day one?
- Would you want a public SDK, event schemas, or just a demo first?

**No sales** — we’re a month out from UI. Just trying to get early‑adopter feedback. GitHub discussion here: <link>

---

# GitHub Discussion (pinned announcement template)

**Title**: RFC: Open‑sourcing plan for Hawkington — meta‑repo now, core later?

Hey folks! We’re getting close to showing Hawkington in public and want to do this right for early adopters.

## Goals
- Invite collaboration early (schemas, SDK, examples)
- Protect core agents until we’re ready
- Keep the roadmap and decisions transparent

## Proposal (comment / emoji‑vote welcomed)
**Option A — Meta‑repo now (recommended):**
- Public repo with docs, event taxonomy, SDK, examples, and a demo app
- Core agent implementations stay private for now
- Source‑available or OSS for the SDK; closed core

**Option B — Source‑available core (BUSL/SSPL) for a season:**
- Public code with non‑OSS license that blocks production/hosted use
- Convert to permissive OSS on a date or milestone

**Option C — Fully public, dual‑license:**
- Permissive OSS + commercial license for hosted/enterprise
- Highest adoption, lowest protection (forks inevitable)

## Guardrails we’d enable either way
- Branch protection + signed releases
- CODEOWNERS + review gates
- SECURITY.md + responsible disclosure
- Issue/PR templates + Discussions categories
- Contributor License Agreement (CLA) for non‑trivial PRs

## What we’re planning to open first
- `/docs` (architecture, guardrails)
- `/schemas` (event types, JSON examples)
- `/sdk` (minimal client to write/read the memory bank)
- `/examples` (dashboards, rollup jobs)

## What stays private (for now)
- Decision engines + model weights
- Proprietary heuristics and playbooks

## Questions for you
1) Would a meta‑repo + SDK be enough to try this?
2) What license do you prefer for the SDK (MIT/Apache/BSD)?
3) What license is acceptable for the core while we’re pre‑launch (BUSL/PolyForm/SSPL)?
4) Which examples would help you decide? (dashboards, chaos drills, CI hooks, etc.)

👇 Drop thoughts, nits, or “please don’t do X” below. Early feedback shapes v0.1.

---

# GitHub maneuvering guide (practical, no‑nonsense)

## If you want interest **without** early forks
- Keep the **core** private.
- Publish a **public meta‑repo** with: README, ARCHITECTURE.md, ROADMAP.md, /schemas, /sdk, /examples.
- License the SDK permissively (MIT/Apache‑2.0) to lower friction.
- Use a source‑available license (e.g., BUSL‑1.1) **if** you decide to show core code early.
- You cannot disable forks on a public repo; the defense is licensing + keeping crown jewels private.

## Files to include on day one
- `README.md` (clear positioning, quickstart)
- `ARCHITECTURE.md` (central bank, agents, guardrails)
- `EVENTS.md` or `/schemas/*.json` (typed events)
- `CONTRIBUTING.md` + `CODE_OF_CONDUCT.md`
- `SECURITY.md` (disclosure process)
- `ROADMAP.md` + `RFCs/0001-...`
- `.github/ISSUE_TEMPLATE/*.yml`, `PULL_REQUEST_TEMPLATE.md`, `DISCUSSION_TEMPLATE/*.md`
- `LICENSE` (SDK) + `LICENSE.core` (if SA license later)
- `CODEOWNERS` (review gates)

## Settings to flip
- Branch protection: require PR reviews, status checks, signed commits (optional)
- Dependabot + GH Actions: lint/tests on PRs
- Discussions: categories (Announcements, Q&A, RFCs, Show & Tell)
- Environments: limit who can publish releases

## Launch cadence (your 12‑week plan)
- **Weeks 1–4 (UI/UX build):** Make meta‑repo public. Publish schemas + SDK. Post the dev.to article. Start Discussions.
- **Weeks 5–8 (awareness):** Add demo app + screenshots. Run a small alpha with hand‑picked teams. Post updates.
- **Weeks 9–12 (refine/test):** Consider opening specific agent plugins or playbooks. Lock v0.1 APIs. Prep a changelog + migration notes.

## CTA copy (for repo README)
> **Try the day shift.** Clone the demo, send a few events, and watch a harmony snapshot render. Then tell us what’s missing. We’re here for early adopter feedback, not hype.

