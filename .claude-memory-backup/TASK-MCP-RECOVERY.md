---
name: TASK-MCP-RECOVERY
description: Recover or regenerate .mcp.json with 7 MCP server configurations
type: task
priority: MEDIUM
---

# TASK: Recover/Regenerate .mcp.json

**Owner**: Claude Code or Miles
**Deadline**: March 15, 2026
**Time estimate**: 1-2 hours
**Impact**: Enables MCP tools (Twitter, Reddit, Slack, GitHub, Gmail, Drive, Perplexity)

---

## Current State
- **File**: `/root/.mcp.json`
- **Status**: MISSING
- **Impact**: 7 MCP servers offline → no tool access for those integrations
- **Last known servers**: Twitter, Reddit, Slack, GitHub, Gmail, Drive, Perplexity

---

## PHASE 1: Search for Existing .mcp.json

### 1A. Check Git History
```bash
cd /root
git log --all --full-history -- ".mcp.json"
git show HEAD:.mcp.json  # If in current version
git show <old-commit>:.mcp.json  # If in historical version
```

### 1B. Check Backups
```bash
# Tar backups
tar -tzf /root/*backup*.tar.gz | grep ".mcp.json"
# If found:
tar -xzf /root/openclaw-backup-*.tar.gz .mcp.json -C /tmp/

# Zip backups
unzip -l /root/*.zip | grep ".mcp.json"
```

### 1C. Check Old Locations
```bash
find /root -name ".mcp.json" -o -name ".mcp.json.*"
find /root -name "*mcp*" -type f | head -10
```

### 1D. Search Subdirectories
```bash
grep -r "mcp" /root/openclaw/ --include="*.json" | head -5
# Might find references to MCP config elsewhere
```

---

## PHASE 2: Regenerate from Template (If Not Found)

If not found in Phase 1, create new `.mcp.json` file.

### 2A. Create Base Structure

Create `/root/.mcp.json`:

```json
{
  "mcpServers": {
    "twitter": {
      "command": "npx",
      "args": ["@mcp-servers/twitter"]
    },
    "reddit": {
      "command": "npx",
      "args": ["@mcp-servers/reddit"]
    },
    "slack": {
      "command": "npx",
      "args": ["@mcp-servers/slack"]
    },
    "github": {
      "command": "npx",
      "args": ["@mcp-servers/github"]
    },
    "gmail": {
      "command": "npx",
      "args": ["@mcp-servers/gmail"]
    },
    "google-drive": {
      "command": "npx",
      "args": ["@mcp-servers/google-drive"]
    },
    "perplexity": {
      "command": "npx",
      "args": ["@mcp-servers/perplexity"]
    }
  }
}
```

### 2B. Add Environment Variables

Some MCP servers need credentials in `.env`:

```bash
# .env additions needed
TWITTER_API_KEY=<your-key>
TWITTER_API_SECRET=<your-secret>
TWITTER_ACCESS_TOKEN=<your-token>
TWITTER_ACCESS_SECRET=<your-secret>

REDDIT_CLIENT_ID=<your-id>
REDDIT_CLIENT_SECRET=<your-secret>
REDDIT_USERNAME=<your-username>
REDDIT_PASSWORD=<your-password>

SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=C...

GITHUB_TOKEN=ghp_...

GMAIL_CREDENTIALS=<from GWS setup>

GOOGLE_DRIVE_CREDENTIALS=<from GWS setup>

PERPLEXITY_API_KEY=<your-key>
```

---

## PHASE 3: Test Each MCP Server

### 3A. Verify Installation

```bash
# Check if MCP servers are installed globally
npm list -g | grep -i mcp

# If not found, install
npm install -g @mcp-servers/twitter @mcp-servers/reddit @mcp-servers/slack
```

### 3B. Test Each Server

After restarting gateway, test each integration:

```bash
# Test Twitter
curl -X GET https://gateway.overseerclaw.uk/api/tools/twitter/search \
  -H "X-Auth-Token: <token>" \
  -d '{"query": "AI agents"}'

# Test Reddit
curl -X GET https://gateway.overseerclaw.uk/api/tools/reddit/browse \
  -H "X-Auth-Token: <token>" \
  -d '{"subreddit": "MachineLearning"}'

# Test Slack
curl -X POST https://gateway.overseerclaw.uk/api/tools/slack/message \
  -H "X-Auth-Token: <token>" \
  -d '{"channel": "general", "text": "MCP test"}'

# Test GitHub
curl -X GET https://gateway.overseerclaw.uk/api/tools/github/search \
  -H "X-Auth-Token: <token>" \
  -d '{"query": "openclaw"}'

# Test Gmail (after GWS setup)
curl -X GET https://gateway.overseerclaw.uk/api/tools/gmail/list \
  -H "X-Auth-Token: <token>"

# Test Google Drive (after GWS setup)
curl -X GET https://gateway.overseerclaw.uk/api/tools/drive/list \
  -H "X-Auth-Token: <token>"

# Test Perplexity
curl -X POST https://gateway.overseerclaw.uk/api/tools/perplexity/search \
  -H "X-Auth-Token: <token>" \
  -d '{"query": "latest AI trends"}'
```

---

## PHASE 4: Restart & Verify

### 4A. Restart Gateway

```bash
systemctl restart openclaw-gateway
sleep 5
```

### 4B. Check Logs

```bash
journalctl -u openclaw-gateway -f | grep -i "mcp\|error"
# Should see: "Loading MCP servers..." (no errors)
```

### 4C. Health Check

```bash
curl https://gateway.overseerclaw.uk/health

# Response should include:
{
  "status": "healthy",
  "mcp_servers": {
    "twitter": "connected",
    "reddit": "connected",
    "slack": "connected",
    "github": "connected",
    "gmail": "connected",
    "google-drive": "connected",
    "perplexity": "connected"
  }
}
```

### 4D. List Available Tools

```bash
curl https://gateway.overseerclaw.uk/api/tools/list \
  -H "X-Auth-Token: <token>"

# Should show all 7 servers' tools available
```

---

## MCP Servers Details

| Server | Purpose | Key Tools | Credentials |
|--------|---------|-----------|-------------|
| Twitter | Read/search tweets, follow accounts | search, timeline, tweet | API keys |
| Reddit | Browse subreddits, search posts | browse, search, submit | OAuth token |
| Slack | Send messages, read channels | message, channel_list | Bot token |
| GitHub | Push code, create issues, search repos | push, issue, search | Personal token |
| Gmail | Send/receive emails (after GWS) | send, search, reply | Service account |
| Google Drive | File storage, sharing (after GWS) | list, upload, share | Service account |
| Perplexity | Research API, web search | search, research | API key |

---

## Troubleshooting

### "MCP server not found"
→ Server not installed globally
→ Fix: `npm install -g @mcp-servers/twitter` (etc.)

### "Connection refused"
→ MCP server process not running
→ Fix: Restart gateway: `systemctl restart openclaw-gateway`

### "Authentication failed"
→ API credentials wrong or missing in .env
→ Fix: Check `.env` for correct keys (see Phase 2B)

### "Module not found"
→ .mcp.json syntax error or server name wrong
→ Fix: Validate JSON: `jq . /root/.mcp.json`

### Some servers work, others don't
→ Selective credential issue
→ Fix: Test each individually with curl, check logs

---

## Verification Checklist

- [ ] .mcp.json created/recovered
- [ ] All 7 servers listed in file
- [ ] .env has all needed credentials
- [ ] Gateway restarted
- [ ] No errors in gateway logs
- [ ] All 7 tools show in `/api/tools/list`
- [ ] At least 3 servers respond to test calls
- [ ] Health check shows all "connected"

---

## Success Criteria

✅ `.mcp.json` file exists at `/root/.mcp.json`
✅ All 7 MCP servers configured
✅ Gateway starts without errors
✅ At least 5/7 servers showing as "connected"
✅ Can call at least one tool from each server

---

## Priority Ordering for Demos

For March 20 investor demo, these are most impressive:
1. **GitHub** (show code push/PR creation)
2. **Slack** (show message sending)
3. **Twitter** (show tweet search)
4. **Perplexity** (show research capability)
5. Gmail (less visible, but setup enables PA)
6. Google Drive (less visible)
7. Reddit (less visible)

---

## Time Breakdown

- Search for existing file: 15 min
- Create/recover .mcp.json: 15 min
- Add credentials to .env: 15 min
- Restart and test: 15 min
- **Total**: ~1 hour

---

## Notes

If any server consistently fails:
- Can remove from .mcp.json and re-add later
- Focus on getting 5/7 working by March 15
- Less critical than EdgeBoard + GWS for demo impact

---

**Dependency**: Requires GWS setup (TASK-GWS-OAUTH-SETUP) complete for Gmail/Drive to work.

**Next**: After both .mcp.json and GWS done, PA will be fully functional for demo.
