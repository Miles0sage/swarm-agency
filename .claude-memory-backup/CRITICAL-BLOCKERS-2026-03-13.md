---
name: CRITICAL-BLOCKERS-2026-03-13
description: Urgent blockers blocking investor demos and OpenClaw v5 deployment
type: status
---

# CRITICAL BLOCKERS (March 13, 2026)

**Status**: 3 CRITICAL blockers identified. Investor demo deadline: March 20 (7 days).

---

## 1. BLOCKER: EdgeBoard Dashboard Source Missing (CRITICAL)

**Severity**: CRITICAL
**Timeline**: Must resolve by March 19 (demo day)
**Impact**: Cannot show betting dashboard to investors; revenue demo blocked

### Current State
- Directory: `/root/edgeboard/`
- Contents: `.next/` build artifacts ONLY (no source)
- Status: `.next` produced but source lost
- Build system: Next.js 16.1.6 configured

### Issue
EdgeBoard source code (all `.tsx`, `.ts`, `lib/`, `components/`) is completely missing. Only the build output exists.

### Root Cause Options
1. Source deleted without backup
2. Source in git but not checked out
3. Source on old branch not merged
4. Source on backup/external drive

### Recovery Plan (Priority Order)
```
Option A: Restore from git history
  - Check git log for edgeboard commits
  - git checkout <branch> -- src/

Option B: Restore from backup
  - Check /root/openclaw-backup*.tar.gz
  - Look for recent snapshots

Option C: Rebuild from scratch
  - Reconstruct from memory files + API references
  - Use specifications from: prediction-market-passive-income-plan.md
  - Time: ~2-3 days intensive build
```

### What We Know About EdgeBoard (From Memory)
- **Purpose**: Betting dashboard with live odds & +EV recommendations
- **Tech**: Next.js 16, Tailwind CSS, TypeScript
- **Data sources**:
  - Sports predictions (XGBoost model)
  - Polymarket prices
  - Kalshi markets
  - Sportsbook odds (200+ bookmakers)
- **Features**:
  - Live odds display
  - +EV bet finder
  - P&L tracker
  - Arbitrage alerts
- **Deployment**: Vercel or self-hosted (dashboard.overseerclaw.uk)

### Action Items
- [ ] Search git history: `git log --all --full-history -- "*edgeboard*"`
- [ ] Search backups: `find /root -name "*backup*" -type f | grep -i edge`
- [ ] Check external drives/Google Drive/GitHub private repos
- [ ] If not found by March 16 noon, START REBUILD

---

## 2. BLOCKER: PA Deployment - GWS OAuth Incomplete (HIGH)

**Severity**: HIGH
**Timeline**: Needed for full PA feature demo
**Impact**: PA integrations (Gmail, Calendar, Drive) non-functional

### Current State
- Service: Deployed to `pa.overseerclaw.uk`
- Status: Core works, auth incomplete
- Blocking: Gmail OAuth, Google Calendar, Google Drive

### Missing Credentials
```
.env variables needed:
- GOOGLE_SERVICE_ACCOUNT_JSON
- GOOGLE_WORKSPACE_DOMAIN
- GMAIL_API_CREDENTIALS
- CALENDAR_API_CREDENTIALS
- DRIVE_API_CREDENTIALS
```

### GWS Setup Steps (Checklist)
- [ ] Create service account in Google Cloud Console
- [ ] Download credentials JSON
- [ ] Enable required APIs (Gmail, Calendar, Drive)
- [ ] Configure OAuth consent screen
- [ ] Grant domain-wide delegation
- [ ] Test OAuth flow
- [ ] Deploy .env with credentials

### Action Items
- [ ] Start GWS setup immediately (can parallelize with EdgeBoard recovery)
- [ ] Document step-by-step process in separate TASK file
- [ ] Test with real user email before marking complete

---

## 3. BLOCKER: .mcp.json Missing - MCP Servers Offline (MEDIUM)

**Severity**: MEDIUM
**Timeline**: Needed for Tool Orchestration
**Impact**: 7 MCP servers (Twitter, Reddit, Slack, GitHub, Gmail, Google Drive, Perplexity) offline

### Current State
- Status: File missing from deployment
- Expected location: `/root/.mcp.json`
- Last known: Configured with 7 servers

### Known MCP Servers
1. Twitter (read tweets, timeline)
2. Reddit (browse, search)
3. Slack (send messages, read channels)
4. GitHub (push code, create issues)
5. Gmail (send/receive, search)
6. Google Drive (file storage)
7. Perplexity (research API)

### Recovery/Rebuild
- [ ] Check git history for `.mcp.json` template
- [ ] Regenerate from configuration memory
- [ ] Add to `/root/.mcp.json`
- [ ] Test each server connection
- [ ] Restart gateway: `systemctl restart openclaw-gateway`

### MCP.json Template
```json
{
  "servers": {
    "twitter": { "type": "cwd", "command": "... executable path" },
    "reddit": { ... },
    "slack": { ... },
    "github": { ... },
    "gmail": { ... },
    "google-drive": { ... },
    "perplexity": { ... }
  }
}
```

---

## Timeline to Resolution

### March 14 (Tomorrow)
- [ ] Search for EdgeBoard source everywhere possible
- [ ] Start GWS OAuth setup (Google Cloud Console)
- [ ] Regenerate `.mcp.json`

### March 15-16
- If EdgeBoard found: Deploy & test
- If EdgeBoard NOT found by noon March 16: START REBUILD
- GWS setup: Complete service account creation

### March 17-18
- EdgeBoard rebuild (if needed): Core components
- GWS setup: Test OAuth flow
- .mcp.json: Test all 7 servers

### March 19
- EdgeBoard: Final polish & deploy
- Demo dry-run with all 3 components working

### March 20
- Investor demo (3 working features)

---

## Resource Allocation

### For EdgeBoard Recovery (PRIORITY)
- Time: 2-3 days intensive
- Tools: Git history, backups, rebuild if needed
- Success = working dashboard by March 19

### For GWS/PA Integration
- Time: 1-2 days setup + testing
- Parallel with EdgeBoard if possible
- Can test incrementally

### For .mcp.json
- Time: 2-4 hours
- Lowest priority (least visible)
- Can do during other tasks

---

## Success Criteria for March 20 Demo

✅ EdgeBoard dashboard loads in <2s
✅ Live odds updating (< 1 min lag)
✅ +EV recommendations showing
✅ PA demonstrates email/calendar integration
✅ At least 1 MCP tool working (Slack message or GitHub push)

---

## Questions for Miles

1. **EdgeBoard source**: Do you have it on external drive, Google Drive, or GitHub private repo?
2. **GWS credentials**: Do you have Google Cloud Console access to create service account?
3. **Investor deadline**: Is March 20 firm, or can it move if EdgeBoard recovery takes longer?

---

See: edgeboard-dashboard-status.md, pa-deploy-status.md, openclaw-action-plan-march2026.md
