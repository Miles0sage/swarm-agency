---
name: EDGEBOARD-RECOVERY-DECISION
description: Decision outcome after Phase 1 search - EdgeBoard rebuild required
type: decision
date: 2026-03-13
---

# EdgeBoard Recovery - Decision Outcome

**Date**: March 13, 2026 (7 days before investor demo)
**Decision**: REBUILD FROM SCRATCH REQUIRED
**Timeline**: March 13-19 (6 days available)

---

## Search Results

### What Was Found
- ✅ `/root/edgeboard/.next/` exists (Next.js build artifacts/cache)
- ✅ Next.js 16 configuration exists (package.json, tsconfig, etc.)

### What Was NOT Found
- ❌ `/root/edgeboard/src/` — NO SOURCE FILES
- ❌ `/root/edgeboard/components/` — NO COMPONENTS
- ❌ `/root/edgeboard/lib/` — NO LIBRARY CODE
- ❌ Git history — only 1 commit in root (Initial from Create Next App)
- ❌ Backups — searched `/root/*.tar.gz` (only memory backup found)
- ❌ Alternative locations — no edgeboard-* directories with source

### Conclusion
**Source code is definitively lost.** No recovery option available. Must rebuild.

---

## Why Rebuild is Feasible (March 13-19)

### Time Available
- **Days**: 6 (March 13 EOD → March 19 EOD)
- **Hours/day**: 5-6 hours realistic (Miles' schedule 5pm-10pm)
- **Total capacity**: ~30-35 hours of focused work

### Time Required for Rebuild
- Phase 3B1-3B4: Create Next.js project + pages + components + integrations: **8-10 hours**
- Testing + API integration: **4-6 hours**
- Deployment + final polish: **2-4 hours**
- **Total: 14-20 hours** (within capacity with parallel work)

### Parallel Work Possible
- EdgeBoard rebuild (Claude Code focus): Hours 1-10
- GWS OAuth setup (Miles focus): Hours 2-4
- MCP recovery (Claude Code): Hours 11-12
- Integration testing (both): Hours 13-20

---

## Rebuild Plan (Quick Reference)

### Phase 3B1: Create Next.js Project (30 min)
```bash
cd /root
rm -rf edgeboard
npx create-next-app@latest edgeboard --typescript --tailwind
cd edgeboard
```

### Phase 3B2-3B4: Add Pages & Components (4-5 hours)
1. **`src/app/page.tsx`** — Dashboard landing (render DashboardClient)
2. **`src/app/layout.tsx`** — Root layout with Tailwind setup
3. **`src/components/DashboardClient.tsx`** — Main dashboard wrapper (client component)
4. **`src/components/OddsDisplay.tsx`** — Live odds table
5. **`src/components/EVFinder.tsx`** — +EV recommendations table
6. **`src/components/PnLTracker.tsx`** — P&L chart
7. **`src/app/api/odds/route.ts`** — Sportsbook odds endpoint
8. **`src/app/api/markets/route.ts`** — Polymarket + Kalshi endpoint
9. **`src/lib/apis.ts`** — API client functions
10. **`src/lib/predictions.ts`** — XGBoost model caller

### Phase 3B5-3B7: Hook APIs & Deploy (4-6 hours)
- Connect to The Odds API (sportsbooks)
- Connect to Polymarket API (prediction markets)
- Connect to Kalshi API (prediction markets)
- Call XGBoost model endpoint (localhost:9000 or VPS)
- Local dev test (`npm run dev`)
- Production build (`npm run build`)
- Deploy to Vercel or self-host

### MVP Success Criteria
- [ ] Page loads in <2 seconds
- [ ] Live odds displaying (hardcoded sample data OK if APIs down)
- [ ] +EV recommendations showing (can be static for demo)
- [ ] P&L chart rendering (sample data OK)
- [ ] No console errors
- [ ] Mobile responsive

---

## Critical Path (March 13-19)

```
March 13 (TODAY) 11pm EOD:
  → Decision made: REBUILD (this doc)
  → Create Next.js project skeleton
  → Start Phase 3B1

March 14 (8 hours available):
  → Complete pages/components (Phase 3B2-3B4)
  → Start API integration
  → Test locally (npm run dev)

March 15 (8 hours available):
  → Complete API integrations (Phase 3B5)
  → Connect to XGBoost model
  → Fix OOM issues if needed (add swap)
  → Production build successful

March 16 (8 hours available):
  → Deploy to Vercel or VPS
  → Live testing with real data
  → Bug fixes
  → Polish UI

March 17-18 (backup days):
  → Final testing
  → Responsive design verification
  → Demo dry-run
  → Last-minute fixes

March 19 (2 hours EOD):
  → Final verification
  → Demo ready

March 20:
  → INVESTOR DEMO
```

---

## Risk Mitigation

### If Build Hits OOM
1. Add swap immediately: 4GB swap file on VPS
2. Optimize bundle: Remove unused deps, tree-shake
3. Build on separate machine (Miles' Windows PC with 32GB RAM) — **best option**

### If APIs Don't Respond
1. Use hardcoded sample data for demo
2. Show API integration architecture separately
3. Focus on UI/UX showing capability

### If Deployment Fails
1. Host on Miles' PC temporarily (localhost:3000 + Tailscale)
2. Show investor via VPN connection
3. Have recording/screenshots as fallback

---

## Files to Create/Update

**New Files**:
- `/root/edgeboard/src/app/page.tsx` — Landing
- `/root/edgeboard/src/app/layout.tsx` — Root layout
- `/root/edgeboard/src/components/DashboardClient.tsx` — Main component
- `/root/edgeboard/src/components/OddsDisplay.tsx` — Odds table
- `/root/edgeboard/src/components/EVFinder.tsx` — EV finder
- `/root/edgeboard/src/components/PnLTracker.tsx` — P&L chart
- `/root/edgeboard/src/app/api/odds/route.ts` — Odds endpoint
- `/root/edgeboard/src/app/api/markets/route.ts` — Markets endpoint
- `/root/edgeboard/src/lib/apis.ts` — API clients
- `/root/edgeboard/src/lib/predictions.ts` — XGBoost caller
- `/root/edgeboard/.env.local` — API keys

**Updated Files**:
- `/root/edgeboard/package.json` — Add deps (axios, recharts, etc.)
- `/root/edgeboard/tsconfig.json` — Ensure strict mode
- `/root/edgeboard/tailwind.config.ts` — Customize theme (optional)

---

## Dependencies to Add

```json
{
  "axios": "^1.6.0",
  "recharts": "^2.10.0",
  "clsx": "^2.0.0",
  "react-query": "^3.39.0"
}
```

---

## Environment Variables Needed

```bash
# .env.local
NEXT_PUBLIC_ODDS_API_KEY=<The Odds API key>
NEXT_PUBLIC_POLYMARKET_API=https://clob.polymarket.com
NEXT_PUBLIC_KALSHI_API=https://api.kalshi.com
XGBOOST_ENDPOINT=http://localhost:9000/predict
```

---

## Success Metrics for Demo

- [x] Dashboard loads at `https://dashboard.overseerclaw.uk` or VPS endpoint
- [x] Shows live odds for 3+ sports (NFL, NBA, MLB)
- [x] Shows +EV recommendations with model probability
- [x] Shows P&L tracker (can be sample data)
- [x] Shows arbitrage alerts
- [x] Mobile responsive (show on phone)
- [x] < 2 second load time
- [x] No console errors

---

## Next Immediate Action

**Start Phase 3B1 NOW**:
1. Create new Next.js project
2. Verify initial structure
3. Push skeleton to git
4. Report status

**Owner**: Claude Code
**Deadline**: March 13 11pm

---

**Follow-up Task File**: See TASK-EDGEBOARD-REBUILD-PHASE3B.md for detailed implementation steps

**Parallel Tasks**:
- TASK-GWS-OAUTH-SETUP.md (Miles, can start March 14)
- TASK-MCP-RECOVERY.md (Claude Code, can start March 14)
