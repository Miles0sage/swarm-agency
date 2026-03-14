# DashScope / Qwen API Integration Guide

> Last updated: 2026-03-13. Practical guide for using Alibaba Cloud Qwen models via DashScope API.

---

## 1. Account Setup & API Key

1. Go to https://dashscope.console.aliyun.com (international) or sign up at https://www.alibabacloud.com
2. Activate **Model Studio** in the console
3. Create an API key in the DashScope console under API Keys section
4. Store it:
```bash
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxx"
```

## 2. Free Tier

- **1 million free tokens per model** -- valid 90 days after activating Model Studio
- Promotional offers may provide up to **70 million tokens** for new accounts
- Enable "Free quota only" in console to prevent unexpected charges
- Free quota shared between main account and RAM users

## 3. API Endpoints (OpenAI-Compatible)

DashScope is **fully OpenAI-compatible** -- just change `base_url` and `api_key`.

| Region | Base URL |
|--------|----------|
| **Singapore (International)** | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| **US (Virginia)** | `https://dashscope-us.aliyuncs.com/compatible-mode/v1` |
| **China (Beijing)** | `https://dashscope.aliyuncs.com/compatible-mode/v1` |

Authentication: `Authorization: Bearer $DASHSCOPE_API_KEY`

## 4. Available Models & Pricing (USD per 1M tokens)

### Flagship Models

| Model ID | Context | Input $/1M | Output $/1M | Best For |
|----------|---------|------------|-------------|----------|
| `qwen3-max` | 262K | $1.20-$3.00 | $6.00-$15.00 | Complex reasoning, highest quality |
| `qwen3.5-plus` | 1M | $0.40-$0.50 | $2.40-$3.00 | Best price/performance, multimodal |
| `qwen-plus` | 1M | $0.115-$0.689 | $0.287-$6.88 | Great price/performance |
| `qwen3.5-flash` | 1M | $0.029-$0.172 | $0.10-$0.40 | Fast, cheap |
| `qwen-flash` | 1M | $0.022-$0.173 | $0.40-$2.00 | Cheapest option |
| `qwen-turbo` | 1M | ~$0.05 | ~$0.20 | Legacy, budget |

### Reasoning Models

| Model ID | Context | Input $/1M | Output $/1M |
|----------|---------|------------|-------------|
| `qwq-plus` | 131K | $0.80 | $2.40 |
| `qwen3-235b-a22b` | 262K | $0.70 | $2.80 (thinking) / $8.40 (response) |
| `qwen3-32b` | 262K | $0.16 | $0.64 |

### Specialized Models

| Model ID | Context | Use Case |
|----------|---------|----------|
| `qwen3-coder-plus` | 1M | Code generation |
| `qwen-deep-research` | 1M | Web research + report generation |
| `qwen-long-latest` | 10M | Long document analysis |
| `qwen3-vl-plus` | 262K | Vision + text |
| `qwen3-omni-flash` | 65K | Audio + video + text + image |
| `qwen-mt-plus` | 16K | Translation (92 languages) |

### Price Comparison vs OpenAI/Anthropic

| Model | Input $/1M | Output $/1M |
|-------|------------|-------------|
| GPT-4o | $2.50 | $10.00 |
| Claude Sonnet 4.5 | $3.00 | $15.00 |
| **qwen-plus** | **$0.115** | **$0.287** |
| **qwen3.5-flash** | **$0.029** | **$0.10** |

Qwen-Plus is **~20x cheaper** than GPT-4o input, **~35x cheaper** output.

## 5. Code Examples

### Python (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

# Basic chat
completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing briefly."},
    ],
)
print(completion.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "Write a haiku"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Tool calling
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto"
)
```

### Node.js (OpenAI SDK)

```javascript
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.DASHSCOPE_API_KEY,
    baseURL: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
});

// Basic chat
const completion = await client.chat.completions.create({
    model: "qwen-plus",
    messages: [
        { role: "system", content: "You are a helpful assistant." },
        { role: "user", content: "Hello!" },
    ],
});
console.log(completion.choices[0].message.content);

// Streaming
const stream = await client.chat.completions.create({
    model: "qwen-plus",
    messages: [{ role: "user", content: "Tell me a story" }],
    stream: true,
});
for await (const chunk of stream) {
    process.stdout.write(chunk.choices[0]?.delta?.content || "");
}
```

### curl

```bash
curl -X POST https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-plus",
    "messages": [{"role": "user", "content": "Who are you?"}]
  }'
```

## 6. Supported Request Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Required. Model ID (e.g., "qwen-plus") |
| `messages` | array | Required. Conversation history |
| `stream` | boolean | Enable streaming (default: false) |
| `temperature` | float | Sampling temperature [0, 2) |
| `top_p` | float | Nucleus sampling (0, 1.0] |
| `max_tokens` | integer | Max output tokens |
| `tools` | array | Function calling definitions |
| `tool_choice` | string/object | Tool selection policy (auto/none/specific) |
| `response_format` | object | Output format (text/json_object/json_schema) |
| `enable_search` | boolean | Enable built-in web search |
| `seed` | integer | Random seed for reproducibility |

## 7. Drop-in Replacement for OpenAI/Anthropic

YES -- DashScope is a drop-in replacement. Any code using OpenAI SDK works by changing 2 things:

```python
# BEFORE (OpenAI)
client = OpenAI(api_key="sk-openai-key")

# AFTER (DashScope)
client = OpenAI(
    api_key="sk-dashscope-key",
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)
```

Works with: LiteLLM, LangChain, CrewAI, AutoGen, Portkey, OpenRouter, and any OpenAI-compatible framework.

### LiteLLM Integration

```python
import litellm

response = litellm.completion(
    model="dashscope/qwen-plus",
    messages=[{"role": "user", "content": "Hello"}],
    api_key=os.getenv("DASHSCOPE_API_KEY")
)
```

## 8. OpenClaw Integration

To add DashScope as a model provider in OpenClaw:

### Option A: Direct OpenAI-Compatible Config

In the OpenClaw gateway or worker config, add DashScope as a provider:

```json
{
  "providers": {
    "dashscope": {
      "type": "openai-compatible",
      "baseURL": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
      "apiKey": "${DASHSCOPE_API_KEY}",
      "models": {
        "qwen-plus": { "contextWindow": 1000000 },
        "qwen3-max": { "contextWindow": 262144 },
        "qwen3.5-flash": { "contextWindow": 1000000 },
        "qwen-flash": { "contextWindow": 1000000 }
      }
    }
  }
}
```

### Option B: Via LiteLLM Proxy

```yaml
# litellm_config.yaml
model_list:
  - model_name: qwen-plus
    litellm_params:
      model: dashscope/qwen-plus
      api_key: sk-xxx
  - model_name: qwen3-max
    litellm_params:
      model: dashscope/qwen3-max
      api_key: sk-xxx
  - model_name: qwen-flash
    litellm_params:
      model: dashscope/qwen-flash
      api_key: sk-xxx
```

### .env Addition

```bash
# Add to /root/openclaw/.env
DASHSCOPE_API_KEY=sk-your-key-here
```

## 9. Qwen-Agent MCP Integration

Qwen-Agent natively supports MCP servers:

```python
from qwen_agent.agents import Assistant

mcp_config = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "./workspace"]
        },
        "memory": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        }
    }
}

llm_cfg = {'model': 'qwen3-max', 'model_type': 'qwen_dashscope'}

agent = Assistant(
    llm=llm_cfg,
    system_message="You are an intelligent assistant.",
    function_list=[mcp_config]
)
```

Install: `pip install qwen-agent`

## 10. Rate Limits

Rate limits are not explicitly published per-model. General guidance:
- Limits are account-level, increase with usage history
- Contact Alibaba Cloud support for higher limits on production workloads
- Batch API available at **50% discount** for async workloads
- Context cache discounts available for repeated prompts

## 11. Recommended Model Selection for OpenClaw

| Use Case | Model | Why |
|----------|-------|-----|
| Agent orchestration | `qwen-plus` | 1M context, cheap ($0.115 input), tool calling |
| Complex reasoning | `qwen3-max` | Best quality, 262K context |
| Fast/cheap worker tasks | `qwen3.5-flash` or `qwen-flash` | $0.02-0.05 input, 1M context |
| Code generation | `qwen3-coder-plus` | Specialized for code, 1M context |
| Research agent | `qwen-deep-research` | Built-in web search + report generation |
| Long document analysis | `qwen-long-latest` | 10M token context window |
| Vision tasks | `qwen3-vl-plus` | Image understanding |

## 12. Key Advantages

1. **20-35x cheaper** than GPT-4o/Claude for comparable quality
2. **1M token context** on mid-tier models (qwen-plus, qwen-flash)
3. **10M token context** on qwen-long
4. **OpenAI-compatible** -- zero code changes needed
5. **Free tier** -- 1M tokens per model for 90 days
6. **Native MCP support** via Qwen-Agent framework
7. **Tool calling, JSON mode, streaming** all supported
8. **Batch API** at 50% discount for background processing
9. **Multi-region** endpoints (Singapore, US, China)
