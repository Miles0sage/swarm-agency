---
name: ollama-gpu-setup
description: Local Ollama GPU setup and configuration
type: reference
---

# Ollama GPU Setup

## Hardware
- GPU: RTX 4060 (8GB VRAM)
- CPU: Windows 11, 32GB RAM
- Location: Miles's PC (Tailscale VPN accessible)

## Configuration
- Model: Qwen 2.5 Coder 7B
- Framework: Ollama (local inference)
- Network: Tailscale VPN tunnel from VPS

## Integration
- Headless Claude Code via SSH over Tailscale
- Direct local model access from dispatch_pc_ollama tool
- Used for: code analysis, local inference, parallel agent tasks

## SSH Access
- PC accessible via Tailscale private IP
- Tools: dispatch_pc_ollama, check_pc_health, get_dispatch_status
- Alternative: can run Gemini CLI, Aider, Codex locally

## Performance Notes
- RTX 4060 suitable for 7B models
- Qwen 2.5 Coder better performance than Llama2
- Parallel dispatch supported for multi-agent speedup

## Next Steps
- Verify Tailscale VPN connection status
- Check Ollama daemon running on PC
- See ai-coding-automation-research-2026.md for automation patterns
