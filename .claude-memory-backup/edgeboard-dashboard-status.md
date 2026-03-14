---
name: edgeboard-dashboard-status
description: EdgeBoard betting dashboard MVP status and deployment plan
type: project
---

# EdgeBoard Dashboard Status

## Current State
- **Status**: All code written, awaiting build verification
- **Directory**: /root/edgeboard/
- **Directory contents**: .next build output only (source missing)
- **Last update**: 2026-03-13

## Architecture
- **Frontend**: Next.js 16 dashboard
- **Data sources**:
  - Sports predict (XGBoost model)
  - Polymarket prices & trading
  - Kalshi market data
  - Sportsbook odds (200+ bookmakers)
- **Components**:
  - Live odds display
  - +EV bet recommendations
  - P&L tracking
  - Market mispricing alerts

## Known Issues
- **OOM (Out of Memory)**: Build fails with memory constraints
- **Mitigation**: Need larger build environment or build optimization

## Build Verification Needed
1. [ ] Verify source code exists (may be in git history)
2. [ ] Run next build in clean environment
3. [ ] Check for SSR/static generation issues
4. [ ] Optimize bundle size if OOM persists
5. [ ] Test deployed dashboard with live data feeds

## Deployment Plan
- **Target**: Vercel or self-hosted on VPS
- **Env vars**: API keys for odds/market feeds
- **Domain**: dashboard.overseerclaw.uk (if using main VPS)
- **SSL**: Cloudflare certificate (automatic)

## Success Criteria
- Dashboard loads in <2s
- Real-time odds update (< 1 min lag)
- +EV recommendations accurate
- No OOM on production deploy

## Next Steps
1. Locate source code (git restore or backup)
2. Fix OOM issue (optimize or scale build)
3. Deploy to staging
4. Live test with real odds data
5. Show to investors (high-impact demo)

## Revenue Impact
- Demonstrates prediction market expertise
- Attracts sports betting customers
- Proof-of-concept for OpenClaw platform
- Estimated value to raise: $100K+

---

See: prediction-market-passive-income-plan.md, openclaw-action-plan-march2026.md
