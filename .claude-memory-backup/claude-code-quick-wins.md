---
name: claude-code-quick-wins
description: Worktrees, skills, /compact, ultrathink
type: reference
---

# Claude Code Quick Wins

## Shortcut 1: Worktrees for Isolation

### What Is It
Git worktree creates isolated branch working directory without switching branches.

### Use Case
- Multiple features in parallel (no context switching)
- Bug fix while keeping main branch clean
- Experiment without fear of breaking things

### Quick Start
```bash
claude code --worktree my-feature
# Creates .claude/worktrees/my-feature/
# Auto-creates & switches to new branch
```

### Under the Hood
```bash
git worktree add .claude/worktrees/my-feature
# Checkout new branch there
git checkout -b my-feature
```

### Benefit
- **Speed**: No branch switching overhead
- **Safety**: Separate git history per worktree
- **Parallelism**: Work on 3 features simultaneously
- **Cleanup**: Auto-delete when done

### Exit Worktree
```bash
ExitWorktree action: remove  # Delete worktree + branch
# or
ExitWorktree action: keep    # Keep worktree for later
```

## Shortcut 2: Skills (Custom Commands)

### What Is It
Reusable task templates with parameters.

### Example
```bash
/refactor --file src/utils.ts --goal "simplify loops"
/test --suite unit --filter "auth"
/deploy --env staging --service api
```

### Create Custom Skill
Save commonly-used tasks:
```
# skill: test-driven
description: Write test first, then implementation
steps:
  1. Claude Code writes test file
  2. Run test (expect failure)
  3. Implement code
  4. Run test (expect pass)
  5. Refactor for quality
```

### List Skills
```bash
claude code /skills list
# Built-in:
# /refactor - Refactor code
# /test - Run test suite
# /debug - Debug failing code
# /review - Code review
```

### Benefit
- **Consistency**: Same approach every time
- **Predictability**: Task outcome is repeatable
- **Speed**: Less prompt engineering needed
- **Documentation**: Skill serves as process doc

## Shortcut 3: /compact (Token Optimization)

### What Is It
Compress codebase to essential context.

### Usage
```bash
claude code /compact --size small
# Shows top 10 most-relevant files

claude code /compact --size large
# Shows all files, grouped by relevance
```

### How It Works
1. Indexes all files
2. Ranks by relevance to current task
3. Shows "compact view" of codebase
4. Automatically uses compact view in prompts

### Savings
- Small: 80% token reduction (3k → 600 tokens)
- Large: 50% token reduction
- Cost: $0.15 → $0.03 per task

### When to Use
- Working on specific feature (ignore other code)
- Tight token budget
- Pre-caching codebase for day

### Example Output
```
Compact view for "add auth":
src/auth/
├── auth.ts (230 lines, 92% relevant)
├── types.ts (80 lines, 88% relevant)
src/utils/
├── api.ts (150 lines, 45% relevant)
tests/
├── auth.test.ts (200 lines, 95% relevant)
```

## Shortcut 4: Ultrathink Mode (Deep Reasoning)

### What Is It
Claude Code with extended thinking (Claude 3.5 Opus feature).

### Enable
```bash
claude code --ultrathink
# or set in .claude.json:
{
  "model": "claude-3-5-opus",
  "thinking": "extended"
}
```

### What Happens
- Claude takes 5-10x longer to think
- Shows internal reasoning chain
- Produces higher quality code (95%+ accuracy)
- Costs 2-3x more in tokens (but longer thinking = better code)

### When to Use
- Complex architectural decisions
- Subtle bugs that need investigation
- Critical code (payment processing, security)
- Algorithm optimization

### When NOT to Use
- Quick bug fixes (overkill)
- Routine refactoring
- Exploring ideas

### Cost-Benefit
| Situation | Result |
|-----------|--------|
| Normal mode, 5 attempts | 90% quality, $0.50 cost |
| Ultrathink, 1 attempt | 95% quality, $0.15 cost |
| **Winner**: Ultrathink (better quality, lower cost) |

## Shortcut 5: Quick File Operations

### Read File
```bash
claude code --read src/index.ts
# Reads file, displays with line numbers
```

### Read Dir
```bash
claude code --ls src/
# Lists directory structure
```

### Diff Files
```bash
claude code --diff src/old.ts src/new.ts
# Shows line-by-line changes
```

### Git Operations
```bash
claude code --status      # git status
claude code --log --n 5   # git log -5
claude code --branch -a   # git branch -a
```

## Shortcut 6: Configuration File (.claude.json)

### Purpose
Save preferred settings so you don't repeat them.

### Template
```json
{
  "model": "claude-3-5-sonnet",
  "thinking": false,
  "context_window": "compact",
  "auto_commit": true,
  "worktree": false,
  "max_tokens_output": 4000,
  "temperature": 0.7,
  "hooks": {
    "pre_execute": "npm run lint",
    "post_execute": "npm test"
  }
}
```

### Benefit
- One-time setup, then automatic
- Team consistency (commit to git)
- Easy to tweak
- Enables automation

## Quick Wins Cheat Sheet

| Task | Command | Time | Cost |
|------|---------|------|------|
| New feature branch | `/worktree my-feature` | 10s | $0 |
| Refactor + test | `/refactor --goal "simplify"` | 2min | $0.03 |
| Code review | `/review` | 1min | $0.02 |
| Find bug | `ultrathink mode` | 3min | $0.05 |
| Token budget | `/compact --size small` | 30s | $0 |

## Real-World Example

**Scenario**: You need to add feature, refactor old code, fix bug, all in parallel

**Without Quick Wins**:
1. Create branch manually
2. Write feature (5 prompts, $0.30)
3. Switch branches, refactor (3 prompts, $0.20)
4. Switch branches again, debug (4 prompts, $0.25)
5. Merge conflicts (manual)
6. Total: 12 prompts, $0.75, 30 min, stress

**With Quick Wins**:
1. `/worktree feature-a` (feature branch isolated)
2. `/worktree bug-fix` (bug fix branch isolated)
3. `/refactor` in main branch (third task)
4. All run in parallel via /skills
5. Total: 5 focused prompts, $0.20, 10 min, clean

## Setup for OpenClaw PA

### .claude.json for PA Agent
```json
{
  "model": "claude-3-5-sonnet",
  "thinking": false,
  "context_window": "compact",
  "auto_commit": true,
  "worktree": true,
  "hooks": {
    "pre_execute": "npm run lint",
    "post_execute": "npm run test --coverage"
  },
  "skills": {
    "quick-fix": "Minimal change, test immediately",
    "feature": "TDD: test → implementation → optimization",
    "debug": "Ultrathink: deep analysis then fix",
    "review": "Check: quality, perf, security"
  }
}
```

## Pro Tips

1. **Use worktrees for parallel work** (3 features at once)
2. **Set /compact to small** (saves 80% tokens)
3. **Save skills for repetitive tasks**
4. **Use /commit after each skill** (clean git history)
5. **Ultrathink only for hard problems** (2-3x cost justified)
6. **Leverage hooks** (auto-test, auto-lint after changes)
7. **Monitor actual costs** (should be $0.01-0.05 per task)

## Common Mistakes

1. **Not using worktrees** (causes context switching overhead)
2. **Passing full codebase** (use /compact)
3. **Skipping /commit** (history becomes useless)
4. **Always using ultrathink** (wastes money on simple tasks)
5. **Not configuring .claude.json** (repetitive setup)
6. **Ignoring hooks** (manual testing slows you down)

## Next Steps

1. Create `.claude.json` with your preferences
2. Define 3-5 custom skills for your workflow
3. Set up hooks (auto-test, auto-lint)
4. Use worktrees for next multi-branch task
5. Measure actual costs vs. budget

**Expected result**: 50% faster, 40% cheaper coding with Claude Code
