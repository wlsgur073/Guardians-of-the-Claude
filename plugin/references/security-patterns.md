# Security Patterns

Shared reference for `/create` and `/secure` skills. Contains templates for security-related configuration.

## Recommended Deny Patterns

### Essential (always suggest)

```json
"deny": [
  "Read(./.env)",
  "Read(./.env.*)",
  "Edit(./.env)",
  "Edit(./.env.*)",
  "Write(./.env)",
  "Write(./.env.*)",
  "Read(./secrets/)",
  "Edit(./secrets/)",
  "Write(./secrets/)"
]
```

### Extended (suggest when detected)

| Pattern | When to suggest |
| --------- | ---------------- |
| `"Read(./*.pem)"`, `"Read(./*.key)"` | `.pem` or `.key` files exist |
| `"Read(./.aws/)"` | `.aws/` directory exists |

Always merge with existing deny patterns — never overwrite.

## Security Rule File Template

Create at `.claude/rules/security.md`:

```markdown
# Security Rules

## Authentication
- [Detected auth pattern — or ask the user what authentication method the project uses]
- Never log authentication tokens or credentials
- Never hardcode secrets — use environment variables

## Input Validation
- All user input must be validated before use (framework validators, schema libraries, etc.)
- Never trust client-side validation alone — always validate server-side
- Sanitize output to prevent injection attacks when rendering user content

## Secrets Handling
- Never commit `.env`, `.pem`, `.key`, or credential files
- Environment variables are validated at startup (fail fast on missing vars)
- API keys and connection strings must be loaded from environment, never from source code
```

Customize based on detected project patterns (auth middleware, validation libraries, secret management). If nothing detected, use the generic template and note which sections need project-specific details.

## File Protection Hook Template

Add to `.claude/settings.json` under `hooks.PreToolUse`:

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "type": "command",
      "command": "echo \"$CLAUDE_FILE_PATH\" | grep -qE '\\.(env|pem|key)' && echo 'BLOCK: Protected file' && exit 2 || exit 0",
      "statusMessage": "Checking for protected files"
    }
  ]
}
```

Always merge with existing hooks — never overwrite. Ensure `exit 2` (not `exit 1`) for blocking.

## Project-Type Security Checkpoints

| Project type | Additional checks |
| ------------- | ------------------- |
| Web API / backend | Auth middleware, CORS config, rate limiting, input sanitization |
| Frontend web app | XSS prevention, CSP headers, secure cookie settings |
| CLI tool | Input validation, file path traversal prevention |
| Library / package | No hardcoded credentials in examples, secure defaults |

## Permission and Safety Decision Principles

Permission modes (`permissions.defaultMode`) and sandboxing (`sandbox.enabled`) are independent axes — one sets *prompt cadence* (how often Claude asks), the other sets *blast radius* (what damage Claude can do). Pick each based on the work, not as alternatives.

### Permission mode by work type

- **Sensitive or unfamiliar code**: `default` (review every tool action)
- **Iterating on changes you'll review via `git diff`**: `acceptEdits` (auto-approve file edits in working dir)
- **Exploring before changing**: `plan` (no edits permitted)
- **Long autonomous tasks within trusted infrastructure**: `auto` (classifier-based; requires Anthropic API on Max / Team / Enterprise / API plans — not Pro, not Bedrock / Vertex / Foundry; Claude Sonnet 4.6, Opus 4.6, or Opus 4.7 — Max plan: Opus 4.7 only; admin enablement on Team / Enterprise)
- **CI / locked-down scripts**: `dontAsk` (only pre-approved tools)
- **Containerized or VM-only environments**: `bypassPermissions` (no checks; equivalent to `--dangerously-skip-permissions`)

### Sandboxing by blast radius

Sandboxing isolates Bash subprocesses at the OS level. Effective sandboxing requires *both* filesystem and network isolation — without network isolation a compromised agent could exfiltrate sensitive files like SSH keys, and without filesystem isolation it could escape to gain network access. Recommend enabling whenever:
- The user runs Bash commands that touch the filesystem or network
- The platform supports it (macOS / Linux / WSL2; not WSL1)
- The user can install `bubblewrap` + `socat` on Linux

Sandboxing is *complementary* to any permission mode except `bypassPermissions` (which disables all checks). Combining `auto` mode with sandboxing gives autonomous progress with OS-level containment — the strongest practical profile for trusted-infra work.

### Combination guidance (principle, not flowchart)

| Goal | Permission mode | Sandbox |
| ---- | --------------- | ------- |
| Review every action carefully | `default` | optional |
| Edit-review cycles, sandboxed builds | `acceptEdits` | enabled |
| Autonomous progress, trusted org | `auto` | enabled |
| CI / non-interactive | `dontAsk` | enabled |
| Disposable VM / container | `bypassPermissions` | n/a (no checks) |

Adapt advice to the user's plan eligibility, platform, and stated goal — do not present this as an exhaustive flowchart. Plan/model availability and feature surfaces evolve; verify against current canonical docs before binding recommendations.
