---
name: business-strategy
description: Commercialization, cost optimization, and revenue strategy
type: project
---

# Business Strategy

## Monetization Paths (Prioritized)

### Path 1: Prediction Markets (ACTIVE)
- **Sports +EV betting**: $2-5K/month passive (see prediction-market-passive-income-plan.md)
- **Picks-as-a-service**: $5-10K/month recurring (Discord/Telegram)
- **Prediction bonds**: $500-1K/month passive
- **Timeline**: Ship by March 26, 2026

### Path 2: OpenClaw (B2B SaaS)
- **Enterprise pricing**: $1K-10K/month per deployment
- **Target customers**: AI teams, automation agencies, research labs
- **GTM**: Sales demos (EdgeBoard, sports agent)
- **Revenue potential**: $50K-500K ARR

### Path 3: PrestressCalc (B2B)
- **Civil engineering SaaS**: $500-5K/year per customer
- **Target**: Engineering firms, government agencies
- **Competitive advantage**: Web-based, accessible
- **Revenue potential**: $500K-2M ARR (at scale)

### Path 4: Barber CRM (B2B SaaS)
- **Vertical SaaS for barbershops/salons**: $50-500/month
- **Features**: Booking, client management, AI receptionist
- **Target**: 1000 barbershops = $500K-500K ARR
- **Status**: Phase 3 in development

## Cost Structure (Current)

### Fixed Costs
- Claude Max subscription: $200/month (Opus 4.6)
- Codex Plus (GPT-5): $20/month
- VPS (152.53.55.207): $5-10/month (Hetzner)
- Domain & SSL: $5/month
- **Total fixed**: ~$230/month

### Variable Costs
- API calls (Perplexity, Odds, Markets): $50-200/month
- Prediction market trading capital: $100-1000/month (self-funded)
- **Total variable**: $150-1200/month

### Total Monthly Burn
- Conservative: $380/month
- Aggressive: $1430/month
- **Self-funding threshold**: $400+/month from prediction markets

## Revenue Target (First 90 Days)

| Month | Path 1 (Markets) | Path 4 (Barber CRM) | Path 2 (OpenClaw) | Total |
|-------|-----------------|-------------------|-----------------|-------|
| Mar   | $5-10K          | $0                | $0              | $5-10K |
| Apr   | $8-12K          | $5-15K            | $0              | $13-27K |
| May   | $10-15K         | $10-30K           | $5-20K          | $25-65K |

## Cost Optimization

### What's Working
- Claude Max at $200/month (most cost-effective)
- Local Ollama on PC (free inference)
- Free tier Gemini CLI for quick builds
- Open-source tools (Aider, Goose)

### What to Avoid
- Per-API pricing (Perplexity Sonar better than web_search)
- Unnecessary SaaS subscriptions
- Compute-intensive deployments (use Vercel, Cloudflare Workers)

### Strategic Decisions
- No in-house GPU (use PC + PC-based inference)
- No Temporal/Celery complexity (simple queue system works)
- No ML training (use pre-trained models, transfer learning)
- Open-source where possible (saves licensing)

## Funding Strategy
- **Bootstrap path**: Self-fund via prediction markets ($5-10K/month)
- **Fundraising**: At 90-day mark, show MRR + demo
- **Target investors**: AI tools, SaaS, fintech angels
- **Valuation support**: Runway, growth trajectory, market TAM

## Stripe Setup
- Status: TODO
- Needed for: Barber CRM subscriptions, picks-as-a-service
- Integration: Webhook for subscription events

## Key Decisions Made
1. Ship demos BEFORE v5 architecture work
2. Self-fund via sports markets (remove fundraising risk)
3. Multi-product strategy (reduce single-point failure)
4. Cost discipline (bootstrap mentality)

---

See: prediction-market-passive-income-plan.md, openclaw-action-plan-march2026.md
