---
name: everything-claude-code
description: Token optimization, subagents, hooks
type: reference
---

# Everything Claude Code

## Core Concepts

Claude Code is Claude (the LLM) embedded in an IDE with:
- **File system access** (read/write code files)
- **Test execution** (run npm test, pytest, etc.)
- **Git integration** (commit, branch, push)
- **Multi-file awareness** (understands entire codebase)
- **Iterative improvement** (can refine code based on test results)

## Token Optimization

### Problem: High Token Costs
- Each task = 5k-50k input tokens
- Claude 3.5 Sonnet: $0.003/1K input tokens
- Per task: $0.015-0.15 cost
- 100 tasks/day = $1.50-15/day

### Strategy 1: Codebase Caching
**Claude's native file caching** (comes with Sonnet+):
- First 2M tokens cached ($0.30 cost)
- Subsequent calls use cache ($0.003/1K)
- **Savings**: 90% on repeated contexts

**Implementation**:
```
Week 1: Upload full codebase (2M tokens), cost $0.30
Week 2-4: Reuse cache, cost $0.03 per task vs. $0.15
Total: $0.30 + $0.09 (12 tasks) = $0.39 vs. $1.80
```

### Strategy 2: Context Window Reduction
**Only pass relevant files** (not whole codebase):
```python
# BAD: Pass entire repo
context = read_all_files()  # 50k tokens

# GOOD: Pass only relevant files
context = read_files([
    "src/feature.ts",
    "src/types.ts",
    "tests/feature.test.ts"
])  # 5k tokens
```

**Savings**: 90% reduction in context size

### Strategy 3: Prompt Templating
Reuse structured prompts with variable substitution:
```python
prompt = f"""
Task: {task}
File: {filename}
Relevant context:
{context}
Constraints:
- Keep changes minimal
- Run tests after editing
"""
```

### Strategy 4: Streaming Responses
Don't wait for full response, process as tokens arrive:
```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text)  # Print as arrives
        save_partial(text)  # Save progressively
```

**Savings**: Early termination possible

### Token Budget by Task Complexity

| Task | Input | Output | Cost |
|------|-------|--------|------|
| Bug fix (1 file) | 3k | 1k | $0.01 |
| Feature add (3 files) | 8k | 2k | $0.03 |
| Refactor (10 files) | 25k | 5k | $0.08 |
| Design review (whole app) | 50k | 3k | $0.15 |

**Pro tip**: Cache the whole codebase (first use), reuse forever

## Subagents (Multi-Agent Patterns)

### Pattern 1: Hierarchical Delegation
Main agent routes to specialists:

```
Main Agent
├── Code Generator (writes new code)
├── Test Writer (creates tests)
├── Debugger (fixes errors)
└── Reviewer (checks quality)
```

**Implementation**:
```python
def main_task(goal):
    if "write function" in goal:
        return code_generator(goal)
    elif "debug" in goal:
        return debugger(goal)
    elif "test" in goal:
        return test_writer(goal)
```

**Benefit**: Each subagent can use cheaper/faster model

### Pattern 2: Parallel Workers
Multiple agents work simultaneously on independent parts:

```
Main Agent splits task into 3 subtasks
├── Worker 1: Module A
├── Worker 2: Module B
└── Worker 3: Module C

Main Agent: Merge results, resolve conflicts
```

**Speedup**: 2-3x faster (3 parallel vs. sequential)

### Pattern 3: Debate/Consensus
Multiple agents propose solutions, best wins:

```
Agent A: Proposes approach 1
Agent B: Proposes approach 2
Agent C: Evaluates both
→ Selects best approach
```

**Benefit**: Higher quality (90%+ accuracy vs. 85% single)

### Pattern 4: Plan → Execute → Reflect
Multi-step reasoning:

```
Planner: Break goal into steps
Executor: Execute each step
Reviewer: Check quality + suggest improvements
Executor: Refine based on feedback
```

**Ideal for**: Complex tasks (10+ steps)

## Hooks (Integrations)

### Hook Type 1: Pre-execution
Run before Claude Code starts:

```python
@hook.pre_execute
def setup_environment():
    install_dependencies()
    setup_database()
    check_api_keys()
```

### Hook Type 2: Post-execution
Run after Claude Code completes:

```python
@hook.post_execute
def validate_and_deploy(result):
    if validate(result):
        deploy_to_staging()
        run_integration_tests()
    else:
        notify_user("Validation failed")
```

### Hook Type 3: On Error
Handle failures gracefully:

```python
@hook.on_error
def error_handler(error, context):
    if "OutOfMemory" in str(error):
        reduce_batch_size()
        retry()
    elif "Network" in str(error):
        wait_and_retry()
    else:
        escalate_to_human()
```

### Hook Type 4: Custom Tools
Add domain-specific tools:

```python
@hook.register_tool
def calculate_metrics(data):
    """Calculate model performance metrics"""
    return {
        "accuracy": accuracy(data),
        "precision": precision(data),
        "recall": recall(data)
    }
```

## Advanced Usage

### Technique 1: Iterative Refinement Loop
```
1. Claude Code writes code
2. Run tests
3. If tests fail, Claude analyzes failure
4. Refine code
5. Repeat until all tests pass
```

**Best for**: TDD workflows, complex logic

### Technique 2: Prompt Chaining
Break complex task into sequential prompts:

```
Prompt 1: "Analyze the issue"
Prompt 2: "Propose 3 solutions"
Prompt 3: "Implement best solution"
Prompt 4: "Add tests"
Prompt 5: "Optimize performance"
```

**Cost**: 5x separate calls vs. 1 big call
**Benefit**: Better quality (90%+ vs. 75% monolithic)

### Technique 3: Few-Shot Learning
Provide examples of desired behavior:

```
Here are 3 examples of good code:
[Example 1: Small focused function]
[Example 2: With tests]
[Example 3: Optimized version]

Now write a function that:
[Your requirement]
```

**Improvement**: 15-20% accuracy boost

### Technique 4: Rubric-Based Evaluation
Define quality criteria upfront:

```
Code quality rubric:
1. Readability (variable names clear)
2. Performance (no unnecessary loops)
3. Testing (80%+ coverage)
4. Documentation (docstrings present)

Score each criterion 1-10
```

## Performance Metrics

### Baseline (No Optimization)
- **Cost per task**: $0.10
- **Quality**: 80%
- **Speed**: 2 min per task
- **Monthly cost**: $48 (480 tasks)

### With Token Optimization
- **Cost per task**: $0.015 (85% savings)
- **Quality**: 85%
- **Speed**: 1.5 min per task
- **Monthly cost**: $7.20

### With Subagents + Hooks
- **Cost per task**: $0.02 (80% savings)
- **Quality**: 92% (multi-agent voting)
- **Speed**: 0.5 min per task (parallelism)
- **Monthly cost**: $9.60

## Best Practices

1. **Cache the full codebase** first (one-time cost)
2. **Use streaming** for large outputs
3. **Implement hooks** for common patterns
4. **Parallelize** independent subtasks
5. **Use cheaper models** for simple tasks (Haiku/Sonnet)
6. **Save context** between calls (file references, not full content)
7. **Add telemetry** (track success rate, cost per task)
8. **Version prompts** (git-style versioning)

## Common Pitfalls

1. **Passing full codebase every time** (unnecessary token waste)
2. **No error handling** (agent gets stuck on first failure)
3. **Infinite loops** (agent keeps retrying same thing)
4. **No success criteria** (agent doesn't know when to stop)
5. **Mixing concerns** (one agent doing 5 things)
6. **No audit trail** (can't debug what went wrong)

## Integration with OpenClaw PA

### Recommended Setup
```python
class CodeAgent:
    def __init__(self):
        self.cache_codebase()  # One-time, $0.30

    def execute_task(self, task):
        if task.complexity == "simple":
            return self.haiku(task)  # $0.001
        elif task.complexity == "medium":
            return self.sonnet_cached(task)  # $0.015
        else:
            return self.opus_with_subagents(task)  # $0.05

    def haiku(self, task):
        """Small, fast, cheap model"""
        return claude.invoke(model="claude-3-haiku", ...)

    def sonnet_cached(self, task):
        """Use codebase cache (90% savings)"""
        return claude.invoke(model="claude-3-5-sonnet", cache=True)

    def opus_with_subagents(self, task):
        """Complex task: delegate to specialists"""
        return self.subagent_controller.execute(task)
```

**Monthly cost**: $20-30 (vs. $200 with naive usage)
