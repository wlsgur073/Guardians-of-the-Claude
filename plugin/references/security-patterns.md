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
  "Read(./secrets/)"
]
```

### Extended (suggest when detected)

| Pattern | When to suggest |
| --------- | ---------------- |
| `"Edit(./secrets/)"`, `"Write(./secrets/)"` | `secrets/` directory exists |
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
