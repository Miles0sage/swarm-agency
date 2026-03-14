---
name: openclaw-action-plan-march2026
description: 14-day active action plan with 4 parallel tracks
type: project
---

# OpenClaw Action Plan (March 12-26, 2026)

## Status
- ACTIVE NOW: 4 parallel tracks
- Daily schedule: 5pm-10pm Tue-Sun (Mon OFF, Thurs ~9:20pm soccer)
- Decision: Ship use cases BEFORE more v5 architecture work

## 4 Parallel Tracks

### Track 1: Product Demos (PRIORITY)
- EdgeBoard betting dashboard (MVP complete, needs deployment)
- Sports +EV recommendation engine (XGBoost model + live odds)
- Prediction market trading UI (Polymarket + Kalshi)
- Deliverable: Working demos to show investors by March 20

### Track 2: Sports Betting Agency
- Automated sports picks generation
- XGBoost model + line movement analysis
- EV calculation and Kelly-sized recommendations
- Revenue target: Self-fund OpenClaw with sports +EV

### Track 3: Monolith Split (If Time)
- Extract standalone PA module from OpenClaw
- Reduce core gateway complexity
- Enable faster iteration on PA-only features

### Track 4: NotebookLM Additions (If Time)
- Audio note transcription
- Multi-source synthesis
- Timeline generation for complex domains

## Daily Schedule
- **Mon**: OFF
- **Tue-Sun 5-10pm**: Active development
- **Thu**: Soccer ~9:20pm (work around)

## Success Metrics
- 3 live demos by March 20
- $X revenue from sports betting by March 26
- No major production incidents
- 2+ investor pitch opportunities booked

## Current Blockers
- PA deployment (gws setup pending auth)
- Dashboard OOM issues (needs build verification)
- Notion API token missing

## Next Review
March 19, 2026 (mid-sprint checkpoint)

---

See: prediction-market-passive-income-plan.md, openclaw-2week-revenue-plan.md
