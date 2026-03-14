---
name: TASK-EDGEBOARD-RECOVERY
description: Recover EdgeBoard dashboard source code or rebuild from scratch
type: task
priority: CRITICAL
---

# TASK: EdgeBoard Dashboard Source Recovery

**Owner**: Claude Code (or Miles if manual search)
**Deadline**: March 19, 2026 EOD (latest possible date)
**Time estimate**: 2-8 hours (depending on recovery vs rebuild)
**Impact**: CRITICAL for March 20 investor demo

---

## Overview
EdgeBoard source code is missing. Only `.next/` build artifacts exist in `/root/edgeboard/`.
This task focuses on: Search everywhere → If found, deploy. If NOT found by noon March 16, rebuild.

---

## PHASE 1: Search for Source (Hours 1-2)

### 1A. Git History Search

```bash
# Check local repo history
cd /root
git log --all --full-history -- "*edge*" --name-only

# Restore from git if found
git show <commit-hash>:src/app/dashboard/page.tsx  # Example
git checkout <branch> -- src/  # Restore entire src/
```

**Action**: Search these patterns:
- `*edge*`
- `*board*`
- `*betting*`
- `*dashboard*`

**Success**: Source files appear in `/root/src/` or `/root/edgeboard/`

---

### 1B. Backup Search

Check these locations:
```bash
# Tar backups
ls -lh /root/*backup* /root/*bak* /root/*.tar.gz

# Common backup names
find /root -maxdepth 1 -name "*openclaw*backup*" -o -name "*edgeboard*"
find /root -maxdepth 1 -name "*2026-03*" -type f

# Old directories
ls -la /root/openclaw-*/
ls -la /root/edgeboard-*/
```

**Action**: If found, extract:
```bash
tar -xzf /root/openclaw-backup-20260313*.tar.gz -C /tmp/
# Then restore src/ from extraction
```

---

### 1C. External Storage/Cloud Check

Ask Miles:
- [ ] Do you have on Google Drive? (share link/folder)
- [ ] Do you have on GitHub private repo? (clone specific branch)
- [ ] Do you have on external SSD/backup drive?
- [ ] Do you have on another VPS/server?

**Action**: Download/pull from source if found

---

### 1D. Reconstruct from .next Build Artifacts

The `.next/` folder contains compiled output. Might be able to reverse-engineer:

```bash
# Check .next structure
ls -la /root/edgeboard/.next/

# Look for source maps (*.js.map)
find /root/edgeboard/.next -name "*.map" | head -5

# Extract sources from sourcemaps if available
# (low success rate, but worth checking)
```

**Success likelihood**: 10% (modern Next.js bundling makes reverse-engineering hard)

---

## PHASE 2: Decision Point (Hour 3)

**If source found in Phase 1:**
- Deploy immediately
- Skip to PHASE 3: Deploy & Verify

**If source NOT found by noon March 16:**
- Proceed to PHASE 3: Rebuild from Scratch

---

## PHASE 3A: Deploy & Verify (If Found)

### 3A1. Setup Source Directory

```bash
# Check current state
ls -la /root/edgeboard/
# Should show: src/, components/, lib/, package.json, tsconfig.json, etc.

# If source in /tmp or external location:
cp -r /path/to/recovered/src /root/edgeboard/
cp -r /path/to/recovered/components /root/edgeboard/
cp -r /path/to/recovered/lib /root/edgeboard/
```

### 3A2. Install Dependencies

```bash
cd /root/edgeboard/
npm install  # or: bun install
```

**Expected output**: `added X packages in Ys`

### 3A3. Build & Test

```bash
# Development mode first
npm run dev

# Should start on localhost:3000
# Open: http://localhost:3000 (from VPS)
# Test: Can you see dashboard? Live odds? Recommendations?
```

### 3A4. Production Build

```bash
# This is where OOM might happen
npm run build

# If OOM error:
#   Option A: Increase swap: fallocate -l 4G /swapfile && swapon /swapfile
#   Option B: Optimize bundle (remove unused deps)
#   Option C: Build on separate machine with more RAM
```

### 3A5. Deploy

```bash
# Option 1: Deploy to Vercel (simplest)
npm install -g vercel
vercel deploy --prod
# Follow prompts, connect to dashboard.overseerclaw.uk

# Option 2: Self-hosted on VPS
npm run build
npm run start
# Configure systemd service

# Option 3: Docker
docker build -t edgeboard .
docker run -p 3000:3000 edgeboard
```

### 3A6. Verify

```bash
# Check live deployment
curl https://dashboard.overseerclaw.uk/

# Should return HTML (not error)
# Should load in browser in <2s
# Should show live odds/markets
```

---

## PHASE 3B: Rebuild from Scratch (If Not Found)

**Timeline**: Start March 16 noon, complete by March 19 EOD

**Approach**:
- Use Next.js 16 + Tailwind CSS
- Integrate existing XGBoost sports model
- Hook into Polymarket, Kalshi, sportsbook APIs
- Minimal MVP for demo

### 3B1. Create Next.js Project

```bash
rm -rf /root/edgeboard
cd /root
npx create-next-app@latest edgeboard --typescript --tailwind
cd edgeboard
```

### 3B2. Add Essential Pages

Create these files:

**`src/app/page.tsx`** - Dashboard landing
```tsx
import DashboardClient from '@/components/DashboardClient'

export default function Home() {
  return <DashboardClient />
}
```

**`src/app/api/odds/route.ts`** - Live odds endpoint
```typescript
export async function GET() {
  // Fetch from sportsbook API
  // Return JSON: { sport, teams, odds, recommendation }
  return Response.json({ ... })
}
```

**`src/app/api/markets/route.ts`** - Prediction markets
```typescript
export async function GET() {
  // Fetch Polymarket + Kalshi prices
  // Return JSON: { markets, prices, arbitrage_opportunities }
  return Response.json({ ... })
}
```

### 3B3. Add Components

**`src/components/DashboardClient.tsx`** - Main dashboard
- Display live sports odds
- Show +EV recommendations
- Display P&L tracker
- Show arbitrage alerts

**`src/components/OddsDisplay.tsx`** - Odds table
**`src/components/EVFinder.tsx`** - +EV recommendations
**`src/components/PnLTracker.tsx`** - P&L over time

### 3B4. Hook in XGBoost Model

```typescript
// src/lib/predictions.ts
import { spawn } from 'child_process'

export async function predictGame(game: Game) {
  // Call XGBoost model (running on VPS)
  const result = await fetch('http://localhost:9000/predict', {
    method: 'POST',
    body: JSON.stringify(game)
  })
  return result.json()
}
```

### 3B5. Add API Integrations

```typescript
// src/lib/apis.ts
export const sportsOdds = {
  fetch: async () => { /* Call The Odds API */ }
}

export const polymarket = {
  fetch: async () => { /* Call Polymarket API */ }
}

export const kalshi = {
  fetch: async () => { /* Call Kalshi API */ }
}
```

### 3B6. Test Locally

```bash
npm run dev
# Should load on http://localhost:3000
# Should show sample data for markets/odds
```

### 3B7. Build & Deploy

```bash
npm run build
npm run start

# Deploy to Vercel or self-host
```

---

## Decision Matrix (Which Path?)

| Scenario | Action | Time |
|----------|--------|------|
| Source found in git/backup by March 15 | Deploy existing | 2-4 hours |
| Source found externally (Drive/GitHub) | Download + deploy | 4-6 hours |
| Source not found by March 16 noon | Rebuild from scratch | 6-8 hours |
| OOM during build | Add swap + retry | 1 hour |
| Rebuild + OOM | Build on separate PC/VPS | 2-4 hours |

---

## Success Criteria

✅ Dashboard URL loads
✅ Live odds displaying (updates < 1 min)
✅ +EV recommendations showing
✅ P&L tracker working
✅ No console errors
✅ Page loads in < 2 seconds
✅ Mobile responsive (show on phone)
✅ Investor can interact and explore

---

## Fallback if March 19 Seems Impossible

If not recovered/rebuilt by March 18 EOD:
- Show screenshots/recording instead of live demo
- Show XGBoost model + API integrations separately
- Focus investor demo on PA + OpenClaw gateway instead
- Schedule full dashboard demo for March 25

---

## Daily Checkpoint

**March 14**: Phase 1 complete (search done, decision made)
**March 15**: Phase 3 started (deploy or rebuild)
**March 16**: Build/deployment in progress, testing
**March 17**: Final polish, bug fixes
**March 18**: QA pass, responsive testing
**March 19**: Ready for demo
**March 20**: Demo day

---

## Debugging Notes

If build fails with OOM:
```bash
# Check available memory
free -h

# Add 4GB swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Retry build
npm run build
```

If APIs not responding:
```bash
# Check endpoints
curl https://api.sportsdata.io/...
curl https://clob.polymarket.com/...

# Verify API keys in .env
cat .env | grep -i "api_key"
```

If page won't load:
```bash
# Check logs
npm run build 2>&1 | tail -50
npm run start -- --debug

# Browser DevTools: F12 → Console for errors
```

---

## Success Tracking
- [ ] Source location determined
- [ ] Source recovered OR rebuild started
- [ ] Dependencies installed
- [ ] Build successful
- [ ] All 3 data sources connected (sports, polymarket, kalshi)
- [ ] Deployed to dashboard.overseerclaw.uk
- [ ] Live testing complete
- [ ] Investor demo ready

---

**Timeline**: Start IMMEDIATELY. Aim for completion by March 17 (2-day buffer before demo).

**Next**: If recovered, skip to deployment. If rebuilding, coordinate with TASK-GWS-OAUTH-SETUP (can run parallel).
