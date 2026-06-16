---
name: github-pr-management
description: "Complete GitHub PR management workflow: auth, repo management, issues, code review, PR lifecycle, CI/CD, and codebase inspection."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, Issues, Code-Review, CI/CD, Git, Workflow]
    related_skills: []
---

# GitHub PR Management — Complete Workflow

A comprehensive guide to all phases of GitHub workflow management. This skill consolidates authentication, repository operations, issue management, code review, PR lifecycle, CI/CD, and codebase analysis into one unified workflow.

## Table of Contents

1. [Authentication](#authentication)
2. [Repository Management](#repository-management)
3. [Issue Management](#issue-management)
4. [Code Review](#code-review)
5. [PR Lifecycle](#pr-lifecycle)
6. [CI/CD & Merge](#ci-cd--merge)
7. [Codebase Inspection](#codebase-inspection)

---

## Authentication

See `references/github-auth-guide.md` for detailed authentication procedures.

### Quick Auth Detection

```bash
# Determine which method to use throughout this workflow
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # Ensure we have a token for API calls
  if [ -z "$GITHUB_TOKEN" ]; then
    if _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"
```

### Extract Owner/Repo from Git Remote

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

## Repository Management

### Cloning Repositories

Cloning is pure `git` — works identically either way:

```bash
# Clone via HTTPS
git clone https://github.com/owner/repo-name.git

# Clone into specific directory
git clone https://github.com/owner/repo-name.git ./my-local-dir

# Shallow clone (faster)
git clone --depth 1 https://github.com/owner/repo-name.git

# Clone specific branch
git clone --branch develop https://github.com/owner/repo-name.git

# Clone via SSH
git clone git@github.com:owner/repo-name.git
```

### Creating Repositories

**With gh:**

```bash
# Create a public repo and clone it
gh repo create my-new-project --public --clone

# Private, with description and license
gh repo create my-new-project --private --description "A useful tool" --license MIT --clone

# Under an organization
gh repo create my-org/my-new-project --public --clone

# From existing local directory
cd /path/to/existing/project
gh repo create my-project --source . --public --push
```

**With git + curl:**

```bash
# Create the remote repo via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{
    "name": "my-new-project",
    "description": "A useful tool",
    "private": false,
    "auto_init": true,
    "license_template": "mit"
  }'

# Clone it
git clone https://github.com/$GH_USER/my-new-project.git
cd my-new-project

# -- OR -- push an existing local directory to the new repo
cd /path/to/existing/project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/$GH_USER/my-new-project.git
git push -u origin main
```

### Forking Repositories

**With gh:**

```bash
gh repo fork owner/repo-name --clone
```

**With git + curl:**

```bash
# Create the fork via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo-name/forks

# Wait for GitHub to create it, then clone
sleep 3
git clone https://github.com/$GH_USER/repo-name.git
cd repo-name

# Add the original repo as "upstream" remote
git remote add upstream https://github.com/owner/repo-name.git
```

### Keeping a Fork in Sync

```bash
# Pure git — works everywhere
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

---

## Issue Management

### Viewing Issues

**With gh:**

```bash
gh issue list
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue list --search "authentication error" --state all
gh issue view 42
```

**With curl:**

```bash
# List open issues
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:
        labels = ', '.join(l['name'] for l in i['labels'])
        print(f\"#{i['number']:5}  {i['state']:6}  {labels:30}  {i['title']}\")"
```

### Creating Issues

**With gh:**

```bash
gh issue create \
  --title "Login redirect ignores ?next= parameter" \
  --body "## Description
After logging in, users always land on /dashboard.

## Steps to Reproduce
1. Navigate to /settings while logged out
2. Get redirected to /login?next=/settings
3. Log in
4. Actual: redirected to /dashboard (should go to /settings)

## Expected Behavior
Respect the ?next= query parameter." \
  --label "bug,backend" \
  --assignee "username"
```

**With curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues \
  -d '{
    "title": "Login redirect ignores ?next= parameter",
    "body": "## Description\nAfter logging in, users always land on /dashboard.\n\n## Steps to Reproduce\n1. Navigate to /settings while logged out\n2. Get redirected to /login?next=/settings\n3. Log in\n4. Actual: redirected to /dashboard\n\n## Expected Behavior\nRespect the ?next= query parameter.",
    "labels": ["bug", "backend"],
    "assignees": ["username"]
  }'
```

### Managing Issues (Add Labels, Assign, Comment, Close)

**With gh:**

```bash
# Add/Remove labels
gh issue edit 42 --add-label "priority:high,bug"
gh issue edit 42 --remove-label "needs-triage"

# Assignment
gh issue edit 42 --add-assignee username
gh issue edit 42 --add-assignee @me

# Comment
gh issue comment 42 --body "Investigated — root cause is in auth middleware."

# Closing
gh issue close 42
gh issue close 42 --reason "not planned"
gh issue reopen 42
```

**With curl:**

```bash
# Add labels
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels \
  -d '{"labels": ["priority:high", "bug"]}'

# Remove a label
curl -s -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels/needs-triage

# Comment
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/comments \
  -d '{"body": "Investigated — root cause is in auth middleware."}'

# Close
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  -d '{"state": "closed", "state_reason": "completed"}'
```

---

## Code Review

### Reviewing Local Changes (Pre-Push)

```bash
# Get the diff
git diff main...HEAD

# File names only
git diff main...HEAD --name-only

# Stat summary
git diff main...HEAD --stat

# Check for common issues
git diff main...HEAD | grep -n "print(\\|console\\.log\\|TODO\\|FIXME\\|HACK\\|XXX\\|debugger"
```

### Reviewing a Pull Request on GitHub

**With gh:**

```bash
gh pr view 123
gh pr diff 123
gh pr diff 123 --name-only
```

**With git + curl:**

```bash
PR_NUMBER=123

# Get PR details
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "
import sys, json
pr = json.load(sys.stdin)
print(f\"Title: {pr['title']}\")
print(f\"Author: {pr['user']['login']}\")
print(f\"Branch: {pr['head']['ref']} -> {pr['base']['ref']}\")
print(f\"State: {pr['state']}\")
print(f\"Body:\n{pr['body']}\")"

# List changed files
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/files \
  | python3 -c "
import sys, json
for f in json.load(sys.stdin):
    print(f\"{f['status']:10} +{f['additions']:-4} -{f['deletions']:-4}  {f['filename']}\")"
```

### Check Out PR Locally for Full Review

```bash
# Fetch the PR branch and check it out
git fetch origin pull/123/head:pr-123
git checkout pr-123

# Now you can use read_file, search_files, run tests, etc.
```

### Leave Comments on a PR

**General PR comment — with gh:**

```bash
gh pr comment 123 --body "Overall looks good, a few suggestions below."
```

### Leave Inline Review Comments

**Single inline comment — with curl:**

```bash
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments \
  -d "{\"body\": \"This could be simplified with a list comprehension.\", \"path\": \"src/auth/login.py\", \"commit_id\": \"$HEAD_SHA\", \"line\": 45, \"side\": \"RIGHT\"}"
```

### Submit a Formal Review

**With gh:**

```bash
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
gh pr review 123 --comment --body "Some suggestions, nothing blocking."
```

**With curl — atomic review with multiple inline comments:**

```bash
HEAD_SHA=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews \
  -d "{
    \"commit_id\": \"$HEAD_SHA\",
    \"event\": \"COMMENT\",
    \"body\": \"Code review from Hermes Agent\",
    \"comments\": [
      {\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"Use parameterized queries to prevent SQL injection.\"},
      {\"path\": \"src/models/user.py\", \"line\": 23, \"body\": \"Hash passwords with bcrypt before storing.\"},
      {\"path\": \"tests/test_auth.py\", \"line\": 1, \"body\": \"Add test for expired token edge case.\"}
    ]
  }"
```

---

## PR Lifecycle

### Branch Creation

```bash
# Make sure you're up to date
git fetch origin
git checkout main && git pull origin main

# Create and switch to a new branch
git checkout -b feat/add-user-authentication
```

### Making Commits

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

### Pushing and Creating a PR

**With gh:**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{\"title\": \"feat: add JWT-based user authentication\", \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\", \"head\": \"$BRANCH\", \"base\": \"main\"}"
```

### Monitoring CI Status

**With gh:**

```bash
# One-shot check
gh pr checks

# Watch until all checks finish (polls every 10s)
gh pr checks --watch
```

**With git + curl:**

```bash
# Get the latest commit SHA on the current branch
SHA=$(git rev-parse HEAD)

# Query the combined status
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Overall: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"
```

### Merging

**With gh:**

```bash
# Squash merge + delete branch (cleanest for feature branches)
gh pr merge --squash --delete-branch

# Enable auto-merge (merges when all checks pass)
gh pr merge --auto --squash --delete-branch
```

**With git + curl:**

```bash
PR_NUMBER=<number>

# Merge the PR via API (squash)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# Switch back to main locally
git checkout main && git pull origin main
git branch -d $BRANCH
```

---

## CI/CD & Merge

### Check CI Status

See the "Monitoring CI Status" section in the PR Lifecycle section above.

### Auto-Fixing CI Failures

When CI fails, diagnose and fix:

### Step 1: Get Failure Details

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

# List workflow runs on this branch
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f\"Run {r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# Get failed job logs (download as zip, extract, read)
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

### Step 2: Fix and Push

After identifying the issue, use file tools (`patch`, `write_file`) to fix it:

```bash
git add <fixed_files>
git commit -m "fix: resolve CI failure in <check_name>"
git push
```

### Auto-Fix Loop Pattern

When asked to auto-fix CI, follow this loop:

1. Check CI status → identify failures
2. Read failure logs → understand the error
3. Use `read_file` + `patch`/`write_file` → fix the code
4. `git add . && git commit -m "fix: ..." && git push`
5. Wait for CI → re-check status
6. Repeat if still failing (up to 3 attempts, then ask the user)

---

## Codebase Inspection

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios using `pygount`.

### When to Use

- User asks for LOC (lines of code) count
- User wants a language breakdown of a repo
- User asks about codebase size or composition
- User wants code-vs-comment ratios
- General "how big is this repo" questions

### Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

### Basic Summary (Most Common)

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories.

### Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

### Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

### Interpreting Results

The summary table columns:
- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:
- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

---

## References

- `references/github-auth-guide.md` — Detailed authentication procedures
- `references/review-output-template.md` — Code review output template
- `references/ci-troubleshooting.md` — CI failure troubleshooting guide
- `references/conventional-commits.md` — Conventional commits reference
- `templates/pr-body-bugfix.md` — Bugfix PR body template
- `templates/pr-body-feature.md` — Feature PR body template
- `templates/bug-report.md` — Bug report template
- `templates/feature-request.md` — Feature request template

---

## Quick Reference Table

| Action | gh | git + curl |
|--------|-----|-----------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `curl POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `curl POST /repos/o/r/forks` + `git clone` |
| List issues | `gh issue list` | `curl GET /repos/o/r/issues` |
| Create issue | `gh issue create ...` | `curl POST /repos/o/r/issues` |
| View PR diff | `gh pr diff` | `git diff main...HEAD` (local) or `curl .../pulls/N/files` |
| Add comment | `gh pr comment N --body ...` | `curl POST .../issues/N/comments` |
| Request review | `gh pr edit N --add-reviewer user` | `curl POST .../pulls/N/requested_reviewers` |
| Close PR | `gh pr close N` | `curl PATCH .../pulls/N` |
| Check out someone's PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |
| Merge PR | `gh pr merge --squash --delete-branch` | `curl PUT .../pulls/N/merge` + `git push --delete` |
| Check CI | `gh pr checks` | `curl GET .../commits/SHA/status` |
| Rerun CI | `gh run rerun ID` | `curl POST .../runs/ID/rerun` |
| Set secret | `gh secret set KEY` | `curl PUT /repos/o/r/actions/secrets/KEY` (+ encryption) |
| Repo info | `gh repo view o/r` | `curl GET /repos/o/r` |
| Code review | `gh pr view N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |
| Issues management | `gh issue edit N --...` | `curl PATCH/POST .../issues/N/*` |

---

## Common Pitfalls

1. **Treating Codex self-report as verification** — Always inspect the diff and rerun tests from Hermes.
2. **Running Codex in the user's dirty main checkout** — Always isolate in a worktree/branch.
3. **Letting Codex own Kanban** — Codex may summarize progress, but Hermes writes board state.
4. **Forgetting PMB safety invariants in the prompt** — Missing safety text is a lane setup failure.
5. **Using `/goal` for quick edits** — Prefer `codex exec` unless durable multi-step continuation is needed.
6. **Killing a stuck lane without recording why** — `rejected_reason` must explain the decision.
7. **Accepting broad unrelated cleanup because tests pass** — Reject or cherry-pick only the scoped changes.
8. **Credentials not persisting** — Check `git config --global credential.helper` — must be `store` or `cache`.
9. **Multiple GitHub accounts** — Use SSH with different keys per host alias in `~/.ssh/config`, or per-repo credential URLs.
10. **`gh: command not found` + no sudo** — Use git-only Method 1 above — no installation needed.
11. **Context degradation is real** — AI output quality measurably degrades above 70% context window usage. Monitor with `/context` and proactively `/compact`.

---

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY.
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch.
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly.
4. **`--full-auto` for building** — auto-approves changes within the sandbox.
5. **Background for long tasks** — use `background=true` and monitor with `process` tool.
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks.
7. **Parallel is fine** — run multiple Codex processes at once for batch work.

---

## Environment Variables

| Variable | Effect |
|----------|--------|
| `ANTHROPIC_API_KEY` | API key for authentication (alternative to OAuth) |
| `CLAUDE_CODE_EFFORT_LEVEL` | Default effort: `low`, `medium`, `high`, `max`, or `auto` |
| `MAX_THINKING_TOKENS` | Cap thinking tokens (set to `0` to disable thinking entirely) |
| `MAX_MCP_OUTPUT_TOKENS` | Cap output from MCP servers (default varies; set e.g., `50000`) |
| `CLAUDE_CODE_NO_FLICKER=1` | Enable alt-screen rendering to eliminate terminal flicker |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | Strip credentials from sub-processes for security |
| `GITHUB_TOKEN` | Personal access token for GitHub API calls |
| `HERMES_HOME` | Override Hermes home directory (defaults to `$HOME/.hermes`) |

---

## Verification Checklist

- [ ] GitHub authentication is set up (gh CLI OR git token/SSH)
- [ ] Working directory is a valid git repository
- [ ] Branch naming conventions followed (feat/fix/refactor/docs/ci/)
- [ ] Conventional commit messages used
- [ ] PR body includes summary and test plan
- [ ] CI checks pass before merge
- [ ] Code review checklist completed
- [ ] Inline comments added for critical issues
- [ ] Temporary worktrees and branches cleaned up after merge

---

## Notes

This skill consolidates the following previously separate skills into a comprehensive workflow:

- `github-auth` — Authentication setup and detection
- `github-code-review` — Code review procedures
- `github-issues` — Issue management
- `github-pr-workflow` — PR lifecycle
- `github-repo-management` — Repository operations
- `codebase-inspection` — Codebase analysis

Each subsection references the original skill's detailed content via the `references/` directory for session-specific examples and templates.