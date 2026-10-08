# Security Policy

## About This Repository

This repository contains documentation, templates, and examples for configuring Claude Code, plus the `guardians-of-the-claude` plugin. There are no running services, APIs, or hosted user data to compromise. It does ship executable code: the plugin's `SessionStart` hook (`plugin/hooks/session-start.sh`) runs automatically when a Claude Code session starts, resumes, or forks, the skills run helper scripts in `plugin/references/lib/`, and `templates/advanced/hooks/*.sh` are example hooks that adopters copy. Claude Code runs plugin hooks as shell commands with your full user permissions and outside the sandbox.

However, security concerns still apply: templates and examples that teach insecure practices can propagate vulnerabilities into projects that adopt them.

## Scope

The following are considered security issues in this repository:

- **Insecure configuration patterns** in templates or examples (e.g., overly permissive file permissions, disabled security checks)
- **Security anti-patterns** in example code snippets (e.g., SQL injection, XSS, command injection, hardcoded credentials)
- **Exposed sensitive information** accidentally included in any file (API keys, tokens, secrets, internal URLs)
- **Misleading security guidance** in guides that could lead developers to adopt unsafe practices
- **Unsafe plugin or hook code** — command injection, unsafe handling of hook input JSON, or file reads/writes beyond what the plugin documents (its state directory under `.claude/.plugin-cache/guardians-of-the-claude/local/`, the read-only transcript and `guardians/config.json` reads) in `plugin/hooks/*.sh`, `plugin/references/lib/*.sh`, or `templates/advanced/hooks/*.sh`, or skill instructions that could steer Claude into unsafe actions

The following are **not** security issues (please open a regular issue instead):

- Typos or formatting errors
- Outdated but non-harmful information
- Feature requests or general improvements

Vulnerabilities in Claude Code itself (as opposed to this repository's content) are out of scope here. Do not open an issue or advisory for them in this repository; report them privately to Anthropic as described under [Reporting security issues](https://code.claude.com/docs/en/security#reporting-security-issues) in the Claude Code security docs.

## Reporting

Report security concerns **privately** via GitHub Security Advisories — do not open a public issue for a security report.

To report a security concern:

1. [Open a private security advisory](https://github.com/wlsgur073/guardians-of-the-claude/security/advisories/new)
2. Describe which file contains the insecure pattern
3. Explain the potential impact if the pattern were adopted by a real project
4. Suggest a fix if possible

## Response Process

| Step | Timeline |
| ------ | ---------- |
| Acknowledge report | Within 7 days |
| Review and assess | Within 14 days |
| Fix or respond | Within 30 days |

Reporters will be credited in the commit message that addresses the issue, unless they prefer to remain anonymous.
