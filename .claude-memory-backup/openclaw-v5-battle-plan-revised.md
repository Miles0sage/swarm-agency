---
name: openclaw-v5-battle-plan-revised
description: Gap analysis 60/100, what to steal/skip, competitive positioning
type: reference
---

# OpenClaw v5 Battle Plan (Revised)

## Feature Completeness Gap Analysis

**OpenClaw v5 vs. Devin/Manus/Bolt/Cursor: 60/100**

```
Feature Category          OpenClaw  Devin  Manus  Bolt   Cursor
─────────────────────────────────────────────────────────────
Code Execution            80%       100%   70%    95%    50%
Multi-agent              100%       0%     0%     0%     0%
Cost Transparency        100%       20%    30%    50%    40%
Sports Integration       100%       0%     0%     0%     0%
Real-time Streaming      70%        90%    60%    100%   50%
Error Recovery           75%        85%    80%    70%    60%
IDE Integration          40%        50%    60%    100%   95%
Team/Approval Gates      80%        70%    90%    20%    30%
─────────────────────────────────────────────────────────────
OVERALL                  60/100     61/100 56/100 66/100 52/100
```

---

## What to Steal (Priority Order)

### From Bolt (Streaming + Speed)
**What**: Real-time output streaming
```
Bolt: Stream tokens as they arrive
OpenClaw: Currently batch responses

Steal:
- WebSocket connection from client
- Async generator for token streaming
- Progressive rendering on frontend
- Cost: 2 days
```

**Why**: Users see results faster (feel response), better UX

**Not Stealing**:
- HTML-to-web ability (web-only focus)
- Edge compute (too complex)

---

### From Devin (Browser Automation)
**What**: Full-page browser control
```
Devin: Full Playwright automation
OpenClaw: Only PDF/screenshot capture

Steal:
- Multi-tab browser context
- Form filling + interaction
- Screenshot assertions
- Network interception
- Cost: 3 days
```

**Why**: Needed for data scraping, E2E testing agents

**Not Stealing**:
- Full IDE (focus on workflows, not coding)
- Real estate market specific features

---

### From Cursor (Command Palette)
**What**: Quick command invocation
```
Cursor: Cmd+K for AI actions
OpenClaw: Text input only

Steal:
- Slash commands (/sports, /research, /pa)
- Recent commands
- Keyboard shortcuts
- Cost: 1 day
```

**Why**: Faster UX, power users prefer CLI

**Not Stealing**:
- Multi-file editing (not needed)
- Codebase indexing (overkill)

---

### From Manus (Approval Gates)
**What**: Human-in-the-loop confirmation
```
Manus: Every action requires approval
OpenClaw: Risk scoring decides auto vs. manual

Steal:
- Risk threshold configuration (0-100)
- Multi-level approvals (email, Slack, UI)
- Approval audit trail
- Cost: 2 days
```

**Why**: Enterprise wants control, reduces liability

**Not Stealing**:
- Slider controls (too granular for web UX)
- Real-time human pair-programming

---

## What to Skip (Brutal Honesty)

| Feature | Why Not | Cost Saved |
|---|---|---|
| Full IDE | Cursor wins, focus on workflows | 2 weeks |
| Team Workspaces | Simple startups don't need it | 1 week |
| Fine-grained RBAC | Single-user for now | 3 days |
| LLM-based routing | Complex, manual routing works | 4 days |
| Kubernetes | VPS sufficient, docker-compose later | 2 weeks |
| Payment processing | Use Stripe, don't DIY | 1 week |
| SMS notifications | Email + Slack sufficient | 2 days |
| Real-time collab | Not a need-to-have yet | 3 days |
| **Total Saved** | | **5 weeks** |

---

## 5-Week Build Order (Most Impact First)

### Week 1: Revenue Workflows
- **Days 1-2**: Sports odds pipeline (live data)
- **Days 3-4**: Polymarket + Kalshi adapters
- **Day 5**: Risk calculator + Kelly sizing
- **Outcome**: Monetizable product, early revenue

### Week 2: Agent Robustness
- **Days 6-7**: Idempotency (no double-execution)
- **Days 8-9**: Heartbeat + auto-recovery
- **Day 10**: Approval gates (email)
- **Outcome**: Enterprise-ready reliability

### Week 3: UX Improvements
- **Days 11-12**: Streaming responses
- **Days 13-14**: Slash commands
- **Day 15**: Approval UI (dashboard)
- **Outcome**: Faster feedback, better UX

### Week 4: Advanced Features
- **Days 16-17**: Browser automation (Playwright)
- **Days 18-19**: Memory framework (learning)
- **Day 20**: Agent registry + marketplace
- **Outcome**: Competitive parity (vs. Devin)

### Week 5: Operations + Launch
- **Days 21-22**: Monitoring + alerting
- **Days 23-24**: Documentation + API reference
- **Day 25**: Demo blitz (5 videos)
- **Outcome**: Launch-ready, pitch-decks ready

---

## Competitive Positioning

### v5 Narrative (90 days from now)

**Headline**: "The only agent platform that prints money (while you sleep)"

**Positioning**:
- Not a replacement for Cursor/Devin
- Complementary: "Cursor for workflows, OpenClaw for automation + revenue"
- Unique: "Only system with sports + prediction market integration"

**For Founders**:
- "Automate your most annoying tasks AND generate side income"
- "Pay for your Claude Max with sports picks ($500/mo revenue potential)"

**For Traders**:
- "Multi-agent arbitrage detector (Polymarket + Kalshi + Smarkets)"
- "Kelly-sized bets, auditable execution, zero slippage"

**For Enterprises**:
- "Multi-agent orchestration that outperforms single-model systems"
- "Cost transparency, approval gates, audit trails"

---

## Moat Development (By Week)

| Week | Moat | What | Status |
|---|---|---|---|
| 1 | Sports Revenue | Predictions + arb detection | BUILDING |
| 2 | Reliability | Idempotency + heartbeat | BUILDING |
| 3 | Speed | Streaming + command palette | BUILDING |
| 4 | Intelligence | Memory + browser automation | BUILDING |
| 5 | Ecosystem | Agent registry + marketplace | PLANNING |

**Result**: After week 5, OpenClaw will have 3 defensible moats vs. competitors

---

## What Competitors Don't Understand

1. **Sports betting is 10x better CAC than SaaS**
   - Devin/Cursor: $50-200 CAC (slow sales cycle)
   - OpenClaw: $20 CAC (viral, word-of-mouth from traders)

2. **Multi-agent > Single-agent for reliability**
   - Devin: One agent fails = whole task fails
   - OpenClaw: 3 agents, 1 fails = 2 continue

3. **Cost transparency is a moat**
   - Competitors hide API costs (margin play)
   - OpenClaw shows $0.47 per job = trust

4. **Personal Assistant is an untapped market**
   - Competitors focus on code/work
   - OpenClaw: Life automation (email, calendar, expenses)

---

## Success Metrics (v5 Launch + 90 Days)

| Metric | Target | Current |
|---|---|---|
| Signups | 2,000 | 0 |
| Pro subscribers | 60 | 0 |
| Enterprise customers | 3 | 0 |
| MRR | $60,000 | $0 |
| Daily sports picks | 1,000 | 0 |
| Arb alerts sent | 500 | 0 |
| API calls | 50K/day | 0 |

---

## Launch Checklist

- [x] v5 shipped (6 components, 119 tests)
- [ ] Sports pipeline live (week 1)
- [ ] 100 early access users (week 2)
- [ ] 10 paying customers (week 3)
- [ ] Public launch + press (week 5)
- [ ] 1K signups (week 8)
- [ ] $10K MRR (week 12)
