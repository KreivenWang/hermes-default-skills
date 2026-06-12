---
name: software-development-workflow
description: "Complete software development workflow: planning, testing, execution, debugging, and review."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [development, workflow, planning, testing, debugging, code-review, TDD]
    related_skills: [hermes-agent-skill-authoring, github-pr-workflow, requesting-code-review, github-code-review]
---

# Software Development Workflow

A comprehensive skill covering the complete software development lifecycle with labeled subsections for each phase.

## Table of Contents

1. [Planning](#planning)
2. [Test-Driven Development](#test-driven-development)
3. [Subagent-Driven Execution](#subagent-driven-execution)
4. [Code Review & Verification](#code-review--verification)
5. [Systematic Debugging](#systematic-debugging)
6. [Debugging Tools](#debugging-tools)
7. [Plan Mode](#plan-mode)
8. [Spike / Experiments](#spike--experiments)

---

## Planning

### Overview

Write comprehensive implementation plans assuming the implementer has zero context for the codebase and questionable taste.

### When to Use

**Always use before:**
- Implementing multi-step features
- Breaking down complex requirements
- Delegating to subagents

**Don't skip when:**
- Feature seems simple (assumptions cause bugs)
- You plan to implement it yourself
- Working alone (documentation matters)

### Bite-Sized Task Granularity

**Each task = 2-5 minutes of focused work.**

Every step is one action:
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

### Plan Document Structure

Every plan MUST start with:

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### Task Structure

```markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67`

**Step 1: Write failing test**
```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**
```bash
pytest tests/path/test.py::test_specific_behavior -v
```
Expected: FAIL

**Step 3: Write minimal implementation**
```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**
Expected: PASS

**Step 5: Commit**
```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

### Principles

- **DRY** (Don't Repeat Yourself)
- **YAGNI** (You Aren't Gonna Need It)
- **TDD** (Test-Driven Development)
- **Frequent Commits**

### See Also

- `references/writing-plans.md` — Full writing-plans skill
- `references/test-driven-development.md` — Full TDD workflow
- `references/subagent-driven-development.md` — Full execution framework
- `references/requesting-code-review.md` — Full verification pipeline
- `references/systematic-debugging.md` — Full debugging methodology
- `references/debugging-tools.md` — Full debugging tools reference
- `references/plan-mode.md` — Full plan mode instructions
- `references/spike-experiments.md` — Full spike/experimentation guidance

---

## Test-Driven Development

### Overview

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

### The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

### Red-Green-Refactor Cycle

1. **RED** — Write failing test
2. **Verify RED** — Watch it fail
3. **GREEN** — Minimal code to pass
4. **Verify GREEN** — Watch it pass
5. **REFACTOR** — Clean up

### When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write the wished-for API. Write the assertion first. |
| Test too complicated | Design too complicated. Simplify the interface. |
| Must mock everything | Code too coupled. Use dependency injection. |

### See Also

- `writing-plans` — Plan writing
- `subagent-driven-development` — Execution framework
- `systematic-debugging` — Debug methodology
- `requesting-code-review` — Pre-commit verification

---

## Subagent-Driven Execution

### Overview

Execute implementation plans by dispatching fresh subagents per task with systematic two-stage review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

### The Process

1. **Read and Parse Plan** — Extract all tasks into a todo list
2. **Per-Task Workflow:**
   - Dispatch implementer subagent
   - Dispatch spec compliance reviewer
   - Dispatch code quality reviewer
   - Mark complete
3. **Final Review** — Integration check
4. **Verify and Commit**

### Task Granularity

**Each task = 2-5 minutes of focused work.**

### Red Flags — Never Do These

- Start implementation without a plan
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed critical/important issues
- Dispatch multiple implementation subagents for tasks touching same files
- Skip scene-setting context

### See Also

- `writing-plans` — Plan creation
- `test-driven-development` — Testing discipline
- `requesting-code-review` — Code verification
- `systematic-debugging` — Debug methodology

---

## Code Review & Verification

### Overview

Automated verification pipeline before code lands. Static scans, baseline-aware quality gates, and an independent reviewer subagent.

**Core principle:** No agent should verify its own work. Fresh context finds what you miss.

### When to Use

- After implementing a feature or bug fix, before `git commit`
- When user says "commit", "push", "ship", "verify", or "review before merge"
- After completing a task with 2+ file edits in a git repo

### Verification Steps

1. **Get the diff** — `git diff --cached`
2. **Static security scan** — Check for secrets, SQL injection, etc.
3. **Baseline tests and linting** — Detect regressions
4. **Self-review checklist** — Quick scan
5. **Independent reviewer subagent** — Fresh context review
6. **Evaluate results** — Pass or proceed to auto-fix
7. **Auto-fix loop** — Maximum 2 cycles
8. **Commit** — If all passed

### Reference: Common Patterns to Flag

| Language | Bad | Good |
|----------|-----|------|
| Python | `cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")` | `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))` |
| JavaScript | `element.innerHTML = userInput;` | `element.textContent = userInput;` |

### See Also

- `writing-plans` — Plan creation
- `subagent-driven-development` — Execution framework
- `test-driven-development` — Testing discipline
- `systematic-debugging` — Debug methodology
- `github-code-review` — GitHub PR review

---

## Systematic Debugging

### Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes.

### The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

### The Four Phases

1. **Phase 1: Root Cause Investigation**
   - Read error messages carefully
   - Reproduce consistently
   - Check recent changes
   - Gather evidence in multi-component systems
   - Trace data flow

2. **Phase 2: Pattern Analysis**
   - Find working examples
   - Compare against references
   - Identify differences
   - Understand dependencies

3. **Phase 3: Hypothesis and Testing**
   - Form a single hypothesis
   - Test minimally
   - Verify before continuing

4. **Phase 4: Implementation**
   - Create failing test case
   - Implement single fix
   - Verify fix
   - If 3+ fixes failed: question architecture

### Red Flags — STOP and Follow Process

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "I don't fully understand but this might work"
- **"One more fix attempt" (when already tried 2+)**

### See Also

- `python-debugpy` — Python debugging tools
- `node-inspect-debugger` — Node.js debugging tools
- `debugging-hermes-tui-commands` — TUI-specific debugging
- `test-driven-development` — Testing discipline

---

## Debugging Tools

### Overview

Language-specific debugging tools for Hermes Agent development.

### Python Debugging (debugpy + pdb)

**Three tools, picked by situation:**

| Tool | When |
|------|------|
| `breakpoint()` + pdb | Local, interactive, simplest |
| `python -m pdb` | Launch existing script under pdb |
| `debugpy` | Remote / headless / attach to running process |

**Start with `breakpoint()`.** It's the cheapest thing that works.

**Recipes:**

1. **Local breakpoint** — Add `breakpoint()` in source
2. **Launch script under pdb** — `python -m pdb script.py`
3. **Debug pytest test** — `pytest tests/test.py --pdb --trace`
4. **Post-mortem on exception** — `pdb.post_mortem()`
5. **Remote debug** — `debugpy.listen(("127.0.0.1", 5678))`

**See Also:**
- `node-inspect-debugger` — Node.js debugging
- `debugging-hermes-tui-commands` — TUI debugging

### Node.js Debugging (node-inspect + CDP)

**Two tools, pick one:**

- **`node inspect`** — Built-in, zero install, CLI REPL
- **`chrome-remote-interface`** — Scriptable from Node/Python

**Quick Reference:**

| Command | Action |
|---------|--------|
| `c` or `cont` | continue |
| `n` or `next` | step over |
| `s` or `step` | step into |
| `sb('file.js', 42)` | set breakpoint |
| `bt` | backtrace |
| `repl` | drop into REPL |

**Attaching to running process:**

```bash
# Enable inspector
kill -SIGUSR1 <pid>

# Attach debugger
node inspect -p <pid>
# or
node inspect ws://127.0.0.1:9229/<uuid>
```

**See Also:**
- `python-debugpy` — Python debugging
- `debugging-hermes-tui-commands` — TUI debugging

### TUI-Specific Debugging

**Architecture:**

```
Python backend (hermes_cli/commands.py)     <- canonical COMMAND_REGISTRY
       │
       ▼
TUI gateway (tui_gateway/server.py)         <- slash.exec / command.dispatch
       │
       ▼
TUI frontend (ui-tui/src/app/slash/)        <- local handlers + fallthrough
```

**Common Issues:**

1. **Command shows in TUI but not autocomplete** — Missing from `COMMAND_REGISTRY`
2. **Command shows in autocomplete but doesn't work** — Missing handler in gateway
3. **Command behavior differs between CLI and TUI** — Different implementations
4. **Command persists config but doesn't apply live** — Missing state patch

**See Also:**
- `python-debugpy` — Python debugging
- `node-inspect-debugger` — Node.js debugging

---

## Plan Mode

### Overview

Write markdown plans instead of executing. No code implementation, no file edits (except plan files), no commits.

### Core Behavior

- Plan only for this turn
- Do not implement code
- Do not edit project files except plan markdown
- Do not run mutating terminal commands
- Deliverable: markdown plan saved under `.hermes/plans/`

### Output Requirements

Write a markdown plan that is concrete and actionable. Include:

- Goal
- Current context / assumptions
- Proposed approach
- Step-by-step plan
- Files likely to change
- Tests / validation
- Risks, tradeoffs, and open questions

### Save Location

`.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`

### See Also

- `writing-plans` — Full plan writing (with execution)
- `subagent-driven-development` — Plan execution

---

## Spike / Experiments

### Overview

Throwaway experiments to validate an idea before build.

### When to Use

- Validating a technical approach
- Exploring a new library or framework
- Testing a hypothesis about user behavior
- Investigating a problem domain
- Comparing two approaches

### Spike Guidelines

- **Timebox** — Set a clear limit (e.g., 2 hours)
- **No production code** — Throwaway work
- **Document findings** — What worked, what didn't
- **Decide next steps** — Proceed, pivot, or abandon
- **Clean up** — Delete or archive after decision

### Output

A brief report including:

- Objective / hypothesis
- Approach attempted
- Findings (positive and negative)
- Recommendation (proceed/abandon/pivot)
- Any reusable insights

### See Also

- `writing-plans` — Formal implementation planning
- `test-driven-development` — Production-quality development

---

## References

All referenced subsections are available as separate skills for deep dives:

| Section | Skill Name |
|---------|------------|
| Planning | `writing-plans` |
| TDD | `test-driven-development` |
| Execution | `subagent-driven-development` |
| Code Review | `requesting-code-review` |
| Debugging Methodology | `systematic-debugging` |
| Python Debugging | `python-debugpy` |
| Node.js Debugging | `node-inspect-debugger` |
| TUI Debugging | `debugging-hermes-tui-commands` |
| Plan Mode | `plan` |
| Experiments | `spike` |

---

## Quick Reference

| Phase | Key Actions |
|-------|-------------|
| **Plan** | Write bite-sized tasks, exact paths, complete code |
| **Test** | Write failing test first, watch it fail |
| **Execute** | Fresh subagent per task, two-stage review |
| **Verify** | Static scan + independent reviewer |
| **Debug** | 4 phases: investigate, pattern, hypothesis, fix |
| **Debug Tools** | `breakpoint()` for Python, `node inspect` for Node |

---

**Quality is not an accident. It's the result of systematic process.**