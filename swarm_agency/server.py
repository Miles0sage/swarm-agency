"""FastAPI web server with SSE streaming for swarm-agency.

Run with: uvicorn swarm_agency.server:app --host 0.0.0.0 --port 8000
Or:       swarm-agency serve
"""

import asyncio
import json
import os
import uuid
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

from .agency import Agency
from .types import AgencyRequest, Decision
from .presets import create_full_agency_departments, DEPARTMENT_NAMES
from .streaming import stream_debate, VoteEvent
from .templates import TEMPLATES, create_request

app = FastAPI(
    title="Swarm Agency",
    version="0.5.0",
    description="43 AI agents debate your business decisions across 5 model families",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _create_agency(provider: str = "dashscope", memory: bool = False) -> Agency:
    agency = Agency(
        name="SwarmAgency",
        memory_enabled=memory,
        provider=provider,
    )
    for dept in create_full_agency_departments():
        agency.add_department(dept)
    return agency


# ── SSE Streaming Endpoint ───────────────────────────────────────────

async def _vote_stream(
    question: str,
    context: Optional[str] = None,
    department: Optional[str] = None,
    provider: str = "dashscope",
) -> AsyncGenerator[dict, None]:
    """Async generator yielding SSE events as agents vote."""
    agency = _create_agency(provider, memory=False)

    request = AgencyRequest(
        request_id=f"api-{uuid.uuid4().hex[:8]}",
        question=question,
        context=context,
        department=department,
    )

    # Resolve target departments
    target_depts = agency._resolve_departments(request, None)
    if not target_depts:
        yield {"event": "error", "data": json.dumps({"error": "No departments found"})}
        return

    # Stream votes from all departments
    for dept in target_depts:
        async for event in stream_debate(
            dept.agents, request,
            dept.api_key, dept.base_url,
            department_name=dept.name,
        ):
            yield {
                "event": "vote",
                "data": json.dumps({
                    "agent": event.agent_name,
                    "department": event.department,
                    "position": event.vote.position,
                    "confidence": event.vote.confidence,
                    "reasoning": event.vote.reasoning[:200],
                    "factors": event.vote.factors[:3],
                    "completed": event.votes_so_far,
                    "total": event.total_agents,
                    "elapsed": round(event.elapsed, 2),
                }),
            }

    # Final decision
    decision = await agency.decide(request)
    yield {
        "event": "decision",
        "data": json.dumps(decision.to_dict()),
    }
    yield {
        "event": "done",
        "data": json.dumps({"status": "complete"}),
    }


@app.get("/api/decide/stream")
async def stream_decision(
    question: str = Query(..., description="The question to debate"),
    context: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    provider: str = Query("dashscope"),
):
    """SSE endpoint: streams agent votes as they arrive."""
    return EventSourceResponse(_vote_stream(question, context, department, provider))


@app.get("/api/decide")
async def decide(
    question: str = Query(..., description="The question to debate"),
    context: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    provider: str = Query("dashscope"),
    memory: bool = Query(False),
):
    """Non-streaming endpoint: returns full decision JSON."""
    agency = _create_agency(provider, memory)
    request = AgencyRequest(
        request_id=f"api-{uuid.uuid4().hex[:8]}",
        question=question,
        context=context,
        department=department,
    )
    decision = await agency.decide(request)
    return decision.to_dict()


@app.get("/api/dual-debate")
async def dual_debate_endpoint(
    question: str = Query(...),
    context: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    provider_a: str = Query("dashscope"),
    provider_b: str = Query("openrouter"),
):
    """Run same question through 2 providers, compare results."""
    from .dual_debate import dual_debate, format_dual_result_dict
    result = await dual_debate(question, context, department, provider_a, provider_b)
    return format_dual_result_dict(result)


@app.get("/api/alerts")
async def get_alerts(limit: int = Query(20)):
    """Get recent proactive alerts from agents."""
    from .alerts import get_alert_history
    return {"alerts": get_alert_history(limit)}


@app.get("/api/messages")
async def get_messages(limit: int = Query(20)):
    """Get recent agent-to-agent messages."""
    from .messaging import MessageBus
    bus = MessageBus()
    messages = bus.get_recent(limit)
    bus.close()
    return {"messages": [
        {"from": m.from_agent, "to": m.to_agent, "subject": m.subject,
         "body": m.body, "priority": m.priority, "timestamp": m.timestamp,
         "response": m.response}
        for m in messages
    ]}


@app.get("/api/scheduler/jobs")
async def list_scheduled_jobs():
    """List all scheduled agent jobs."""
    from .scheduler import AgentScheduler
    scheduler = AgentScheduler()
    return {"jobs": [
        {"id": j.job_id, "name": j.name, "schedule": j.schedule,
         "enabled": j.enabled, "last_run": j.last_run,
         "last_result": j.last_result, "run_count": j.run_count}
        for j in scheduler.list_jobs()
    ]}


@app.get("/api/agents")
async def list_agents():
    """List all 43 agents across 10 departments."""
    depts = create_full_agency_departments()
    result = []
    for dept in depts:
        for agent in dept.agents:
            result.append({
                "name": agent.name,
                "department": dept.name,
                "role": agent.role,
                "model": agent.model,
                "expertise": agent.expertise,
                "bias": agent.bias,
            })
    return {"agents": result, "total": len(result)}


@app.get("/api/departments")
async def list_departments():
    """List all 10 departments with descriptions."""
    from .presets import DEPARTMENT_DESCRIPTIONS
    return {
        "departments": [
            {"name": name, "description": DEPARTMENT_DESCRIPTIONS.get(name, "")}
            for name in DEPARTMENT_NAMES
        ]
    }


@app.get("/api/templates")
async def list_templates_api():
    """List available decision templates."""
    return {
        "templates": {
            name: {
                "name": t.name,
                "question_format": t.question_format,
                "departments": t.departments,
                "required_fields": t.required_fields,
            }
            for name, t in TEMPLATES.items()
        }
    }


@app.post("/api/template/{template_name}")
async def decide_from_template(
    template_name: str,
    fields: dict,
    provider: str = Query("dashscope"),
):
    """Create and run a debate from a template."""
    try:
        request = create_request(template_name, **fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    agency = _create_agency(provider, memory=False)
    decision = await agency.decide(request)
    return decision.to_dict()


# ── Minimal Frontend ─────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Swarm Agency - Live Deliberation</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,system-ui,sans-serif;background:#0a0a1a;color:#e0e0e0;padding:2rem;max-width:900px;margin:0 auto}
  h1{color:#00bcd4;margin-bottom:0.5rem}
  .subtitle{color:#666;margin-bottom:2rem}
  .input-group{display:flex;gap:0.5rem;margin-bottom:1rem}
  input,select{flex:1;padding:0.75rem;background:#1a1a2e;color:#fff;border:1px solid #333;border-radius:8px;font-size:1rem}
  button{padding:0.75rem 1.5rem;background:#00bcd4;color:#000;border:none;border-radius:8px;font-size:1rem;cursor:pointer;font-weight:bold}
  button:hover{background:#00e5ff}
  button:disabled{opacity:0.5;cursor:not-allowed}
  #progress{color:#888;margin:1rem 0;font-size:0.9rem}
  .vote{padding:0.75rem 1rem;margin:0.3rem 0;border-radius:8px;background:#1a1a2e;border-left:4px solid #555;animation:fadeIn 0.3s}
  .vote.YES{border-color:#4caf50}.vote.NO{border-color:#f44336}.vote.MAYBE{border-color:#ff9800}.vote.ERROR{border-color:#666}
  .vote .name{font-weight:bold;color:#00bcd4}.vote .dept{color:#666;font-size:0.85rem}
  .vote .pos{font-weight:bold;margin:0 0.5rem}
  .vote .pos.YES{color:#4caf50}.vote .pos.NO{color:#f44336}.vote .pos.MAYBE{color:#ff9800}
  .decision{padding:1.5rem;margin:1.5rem 0;border:2px solid #00bcd4;border-radius:12px;text-align:center}
  .decision h2{font-size:1.5rem;margin-bottom:0.5rem}
  .decision .summary{color:#aaa;margin-top:0.5rem}
  @keyframes fadeIn{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>
<h1>Swarm Agency</h1>
<p class="subtitle">43 AI agents debate your business decisions in real-time</p>
<div class="input-group">
  <input id="q" placeholder="Should we raise a Series A or bootstrap?" autofocus>
  <button id="btn" onclick="startStream()">Debate</button>
</div>
<div class="input-group">
  <input id="ctx" placeholder="Context (optional): Revenue $30k MRR, growing 15%...">
  <select id="dept"><option value="">All Departments</option></select>
</div>
<div id="progress"></div>
<div id="votes"></div>
<div id="result"></div>
<script>
['Strategy','Product','Marketing','Research','Finance','Engineering','Legal','Operations','Sales','Creative']
.forEach(d=>{const o=document.createElement('option');o.value=d;o.textContent=d;document.getElementById('dept').appendChild(o)});

function startStream(){
  const q=document.getElementById('q').value;if(!q)return;
  const ctx=document.getElementById('ctx').value;
  const dept=document.getElementById('dept').value;
  document.getElementById('votes').innerHTML='';
  document.getElementById('result').innerHTML='';
  document.getElementById('btn').disabled=true;
  let url='/api/decide/stream?question='+encodeURIComponent(q);
  if(ctx)url+='&context='+encodeURIComponent(ctx);
  if(dept)url+='&department='+encodeURIComponent(dept);
  const source=new EventSource(url);
  source.addEventListener('vote',e=>{
    const d=JSON.parse(e.data);
    document.getElementById('progress').textContent=d.completed+'/'+d.total+' agents ('+d.elapsed+'s)';
    document.getElementById('votes').innerHTML+=
      '<div class="vote '+d.position+'">'+
      '<span class="name">'+d.agent+'</span> <span class="dept">'+d.department+'</span> '+
      '<span class="pos '+d.position+'">'+d.position+'</span> '+(d.confidence*100).toFixed(0)+'% &mdash; '+
      d.reasoning+'</div>';
    document.getElementById('votes').scrollTop=document.getElementById('votes').scrollHeight;
  });
  source.addEventListener('decision',e=>{
    const d=JSON.parse(e.data);
    const colors={CONSENSUS:'#4caf50',MAJORITY:'#ff9800',SPLIT:'#f44336',DEADLOCK:'#666'};
    document.getElementById('result').innerHTML=
      '<div class="decision" style="border-color:'+(colors[d.outcome]||'#00bcd4')+'">'+
      '<h2>'+d.outcome+': '+d.position+'</h2>'+
      '<div>Confidence: '+(d.confidence*100).toFixed(0)+'%</div>'+
      '<div class="summary">'+d.summary+'</div></div>';
  });
  source.addEventListener('done',()=>{
    source.close();
    document.getElementById('progress').textContent='Complete!';
    document.getElementById('btn').disabled=false;
  });
  source.onerror=()=>{source.close();document.getElementById('btn').disabled=false;
    document.getElementById('progress').textContent='Connection lost. Try again.';};
}
document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter')startStream()});
</script>
</body>
</html>"""
