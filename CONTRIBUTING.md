# Contributing to swarm-agency

## Getting Started

```bash
git clone https://github.com/Miles0sage/swarm-agency.git
cd swarm-agency
pip install -e ".[dev]"
pytest
```

## Adding a New Department

1. Define your agents in `swarm_agency/presets.py` or in your own module
2. Each agent needs: `name`, `role`, `expertise`, `bias`, `system_prompt`, `model`
3. Create a factory function: `create_your_dept(**kwargs) -> Department`
4. Add tests in `tests/test_presets.py`

```python
MY_AGENTS = [
    AgentConfig(
        name="AgentName",
        role="Their Role",
        expertise="what they know",
        bias="how they think differently",
        system_prompt=_make_system_prompt(...),
        model="qwen3-coder-plus",
    ),
]
```

## Adding a New Agent to an Existing Department

1. Add the `AgentConfig` to the relevant list in `presets.py`
2. Use a **different model** from existing agents in that department (model diversity = better decisions)
3. Give it a **clear bias** that creates productive tension with other agents
4. Update the agent count in tests

## Testing

```bash
pytest                    # run all tests
pytest -v                 # verbose output
pytest tests/test_X.py    # run specific test file
```

All PRs must pass existing tests. New features need tests.

## Code Style

- Python 3.10+, type hints where practical
- Dataclasses for data types
- `async/await` for API calls
- Keep files under 200 lines when possible

## PR Process

1. Fork the repo
2. Create a feature branch
3. Write tests first, then implementation
4. Run `pytest` — all tests must pass
5. Open PR with description of what and why
