---
name: pa-deploy-status
description: Personal Assistant deployment, authentication, and integration status
type: project
---

# PA Deployment Status

## Current Deployment
- **Service**: OpenClaw Personal Assistant
- **URL**: pa.overseerclaw.uk
- **Port**: 18789 (via Cloudflare proxy)
- **Status**: Partially deployed, pending auth

## Components

### Gateway Integration
- **Status**: WORKING
- **Service**: systemctl restart openclaw-gateway
- **URL**: gateway.overseerclaw.uk
- **Domains**: gateway, dashboard, pa all configured

### PA Module
- **Status**: DEPLOYED but incomplete
- **Features working**: Core PA tasks, tool invocation
- **Features pending**: Full authentication, all integrations

### GWS Setup
- **Status**: IN PROGRESS
- **Task**: Complete Google Workspace Setup
- **Blockers**:
  - Auth tokens needed (Gmail, Google Drive, Calendar)
  - OAuth flow configuration
  - Scopes validation

## Missing Integrations

### High Priority
- [ ] Gmail OAuth (send/receive emails)
- [ ] Google Calendar (schedule management)
- [ ] Google Drive (file storage)
- [ ] Slack bot permissions (messages, notifications)

### Medium Priority
- [ ] Notion API token (database sync)
- [ ] GitHub OAuth (repo access)
- [ ] MCP server connections (Redis, Twitter, etc.)

### Low Priority
- [ ] Analytics dashboard (Mixpanel, custom)
- [ ] Error tracking (Sentry)
- [ ] Advanced monitoring

## Authentication Checklist
- [ ] OAuth consent screen configured
- [ ] Service account credentials generated
- [ ] API scopes whitelisted
- [ ] Rate limiting configured
- [ ] Token refresh logic tested
- [ ] Fallback auth method (API keys) setup

## GWS (Google Workspace Setup) Procedure
1. Create service account in Google Cloud Console
2. Generate credentials JSON
3. Grant domain-wide delegation
4. Whitelist scopes in Google Workspace admin
5. Test auth flow with real user
6. Deploy credentials to VPS (secure storage)
7. Update .env with credentials
8. Restart PA service

## Deployment Commands
```bash
# Restart gateway with PA updates
systemctl restart openclaw-gateway

# Verify PA is responding
curl https://pa.overseerclaw.uk/health

# Check logs
journalctl -u openclaw-gateway -f
```

## Current Issues
- GWS setup incomplete (auth tokens missing)
- .mcp.json lost/missing (MCP servers offline)
- Some PA tools may fail without Notion/GitHub OAuth

## Next Steps (In Order)
1. [ ] Recover or regenerate .mcp.json
2. [ ] Complete GWS OAuth flow
3. [ ] Deploy credentials securely
4. [ ] Test each PA integration
5. [ ] Monitor for 48h before declaring "complete"
6. [ ] Document runbooks for auth renewal

## Support Contacts
- Cloudflare: gateway.overseerclaw.uk DNS management
- VPS: Hetzner (152.53.55.207 SSH access)
- OAuth: Google Cloud Console (project admin)

---

See: openclaw-architecture.md, mcp-servers-installed.md
