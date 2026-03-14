---
name: error-patterns
description: Hard-won debugging lessons (NEVER repeat these mistakes)
type: reference
---

# Error Patterns & Debugging Lessons

## Critical Mistakes (NEVER Repeat)

### 1. Async/Await Context Switching
**Mistake**: Mixing sync Redis with async FastAPI
```python
# WRONG
async def handler():
    redis.get(key)  # Blocks event loop!
```

**Fix**: Always use async Redis client (redis.asyncio)
```python
# RIGHT
async def handler():
    await redis_async.get(key)
```

**Time Cost**: 4 hours debugging phantom timeouts

---

### 2. Session State Mutation
**Mistake**: Modifying shared session dict without copy
```python
# WRONG
session['state'].update(new_data)  # All jobs see the same state!
```

**Fix**: Deep copy before mutation
```python
# RIGHT
import copy
session_copy = copy.deepcopy(session['state'])
session_copy.update(new_data)
```

**Time Cost**: 3 hours, 8 failed test runs

---

### 3. Token Counting (Off-by-One)
**Mistake**: Over-estimating token counts
```python
# WRONG
tokens = len(prompt.split())  # Returns word count, not tokens
cost = tokens * 0.000002
```

**Fix**: Use actual tokenizer
```python
# RIGHT
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(...)
cost = response.usage.input_tokens * 0.000003
```

**Time Cost**: 2 hours billing debugging

---

### 4. Router Deadlock (Least-Loaded Selection)
**Mistake**: Always routing to same agent if it's "fastest"
```python
# WRONG
agent = min(agents, key=lambda a: a.response_time)  # Always picks fastest!
```

**Fix**: Weight by both load and capability
```python
# RIGHT
scores = [1/a.load - 0.1*a.response_time for a in agents]
agent = agents[scores.index(max(scores))]
```

**Time Cost**: 6 hours, system unresponsive

---

### 5. Git Conflict in Lock Files
**Mistake**: Committing package-lock.json during multi-agent builds
```bash
# WRONG
git add package-lock.json
git commit "update deps"
# Merge conflict headache
```

**Fix**: Lock files in .gitignore for local builds
```bash
# RIGHT
echo "package-lock.json" >> .gitignore
npm ci  # Use lock file without modifying
```

**Time Cost**: 2 hours merge conflict resolution

---

### 6. Cost Tracking Off by Factor of 1000
**Mistake**: Mixing cents and dollars
```python
# WRONG
total_cost = sum([job.cost_usd for job in jobs])  # Some are in cents!
```

**Fix**: Standardize all costs to float dollars
```python
# RIGHT
def to_dollars(cost_any_unit: Union[int,float]) -> float:
    if cost_any_unit > 100:
        return cost_any_unit / 100  # Likely cents
    return cost_any_unit
```

**Time Cost**: 1.5 hours, incorrectly reported 100x billing

---

### 7. Subprocess Zombie Processes
**Mistake**: Not waiting for subprocess cleanup
```python
# WRONG
subprocess.Popen(['python', 'script.py'])  # Orphaned process!
```

**Fix**: Use context manager or explicit wait
```python
# RIGHT
with subprocess.Popen(...) as proc:
    proc.wait(timeout=30)
```

**Time Cost**: OOM errors after 100 jobs

---

### 8. Redis Key Expiration Wildcards
**Mistake**: Trying to pattern-delete with KEYS
```python
# WRONG (SLOW)
for key in redis.keys('job:*'):
    redis.delete(key)  # Blocks Redis!
```

**Fix**: Use SCAN for large keyspaces
```python
# RIGHT
cursor = 0
while True:
    cursor, keys = redis.scan(cursor, match='job:*')
    if keys:
        redis.delete(*keys)
    if cursor == 0:
        break
```

**Time Cost**: 30min Redis timeouts during cleanup

---

## Debugging Playbook

### When agents are slow:
1. Check Redis load: `INFO stats`
2. Check Anthropic rate limits: Look for 429 errors
3. Check Ollama queue: `curl localhost:11434/api/tags`
4. Check session state size: `MEMORY STATS` on bloated sessions
5. Profile with `cProfile` (not guesses)

### When costs spike:
1. Check token counts: `response.usage`
2. Check model selection: Log which agent ran
3. Check retry loops: `for attempt in range(...)` can add up
4. Check cache hits: Is Redis actually being used?
5. Verify billing with Anthropic invoice

### When tests fail randomly:
1. Check for race conditions: `asyncio.gather()` ordering
2. Check fixture cleanup: `@pytest.fixture(autouse=True)`
3. Check timezone assumptions: Always use UTC
4. Check floating-point precision: Use `pytest.approx()`
5. Check mock state: Mocks need reset between tests

---

## Testing Rules

- **Never mock Anthropic in production tests** - Use live calls with small prompts ($0.001 each)
- **Always test async with `pytest-asyncio`** - No bare `asyncio.run()`
- **Cost assertions must be within 10%** - Allow for rate fluctuations
- **Session state tests need isolation** - Each test gets fresh Redis
- **Timeout tests with `pytest.timeout` plugin** - Catch deadlocks

---

## Monitoring Checklist

Before shipping to VPS:

- [ ] All costs logged to Supabase
- [ ] Error handler catches all exceptions (no unhandled rejections)
- [ ] Redis connection pooling enabled
- [ ] Session cleanup on job complete (no memory leak)
- [ ] Agent health check running (detect dead workers)
- [ ] Rate limiting in place (max 10 concurrent jobs)
- [ ] Fallback agent configured (if Opus unavailable)
- [ ] Cost alerts above $10/day
- [ ] PagerDuty integration (if uptime critical)
