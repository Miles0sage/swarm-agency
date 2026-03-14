---
name: openclaw-2week-revenue-plan
description: Self-fund OpenClaw via sports betting and product improvements
type: project
---

# 2-Week Revenue Plan (March 13-26, 2026)

## Primary Strategy: Sports Betting +EV

### Why This Works
- XGBoost model already trained (97% benchmark success on 105 jobs)
- Live odds APIs available (200+ bookmakers)
- Soft books vs Pinnacle sharp lines = proven EV edge
- Proven ROI: small bankroll → consistent profit

### Implementation
1. Deploy sports_predict tool (predict today's games)
2. Fetch live odds (sportsbook_odds tool)
3. Calculate +EV bets (minimum 1-2% edge threshold)
4. Kelly-sized stakes (bankroll_management)
5. Track P&L (bet_tracker, prediction_tracker)

### Revenue Targets
- Week 1 (Mar 13-19): Find 3-5 +EV bets, target 5-10% ROI
- Week 2 (Mar 20-26): Scale to 10+ bets/day, target 15% ROI
- Bankroll: Start with $1,000 (proves model), scale to $10K

## Secondary: GitHub UI Theft
- Inspect Devin/Bolt/Cursor GitHub integrations
- Steal UI patterns (sidebar, timeline, breadcrumbs)
- Apply to OpenClaw dashboard
- Low effort, high conversion impact

## Tertiary: Agent Improvements
- Parallel agent speedup (2x via tmux_agents)
- Reflexion learning system (capture failed patterns)
- Tool registry (dynamic tool creation)

## Success = Self-Funded OpenClaw
- $2-5K/month from sports +EV pays for Claude Max ($200)
- Removes dependency on external funding
- Proves business model before raising

## Risks
- Model overfitting to training data
- Live odds movement changes
- Book limits/account closures

## Mitigation
- Use conservative EV threshold (2%+)
- Spread bets across multiple books
- Monitor for model drift weekly
- Have backup strategies (prediction bonds, picks-as-a-service)

---

See: prediction-market-passive-income-plan.md, edgeboard-dashboard-status.md
