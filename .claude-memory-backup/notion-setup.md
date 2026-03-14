---
name: notion-setup
description: Notion API configuration and IDs
type: reference
---

# Notion Setup

## Status
- .mcp.json configuration file NOT found at /root/.mcp.json
- Notion integration configured via MCP servers (see mcp-servers-installed.md)

## Expected Configuration
When .mcp.json exists, it contains:
- Notion API token
- Database IDs for projects
- Page IDs for key pages (logs, tracking, etc.)

## Known Notion Integrations
- Notion Search & Fetch tools available via MCP
- Supports page creation, database queries, updates
- Used for: project tracking, process logging, documentation

## Next Steps
- Verify Notion API token in .mcp.json if needed
- Check for Notion token in environment or credentials
- See mcp-servers-installed.md for current MCP configuration
