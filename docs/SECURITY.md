# Security Policy

## About This Repository

This repository contains documentation, templates, and examples for configuring Claude Code — **it does not contain executable source code**. There are no running services, APIs, or user data to compromise.

However, security concerns still apply: templates and examples that teach insecure practices can propagate vulnerabilities into projects that adopt them.

## Scope

The following are considered security issues in this repository:

- **Insecure configuration patterns** in templates or examples (e.g., overly permissive file permissions, disabled security checks)
- **Security anti-patterns** in example code snippets (e.g., SQL injection, XSS, command injection, hardcoded credentials)
- **Exposed sensitive information** accidentally included in any file (API keys, tokens, secrets, internal URLs)
- **Misleading security guidance** in guides that could lead developers to adopt unsafe practices

The following are **not** security issues (please open a regular issue instead):

- Typos or formatting errors
- Outdated but non-harmful information
- Feature requests or general improvements

## Reporting

Since this repository contains no executable code or user data, **public reporting via GitHub Issues is appropriate**.

To report a security concern:

1. [Open a new issue](https://github.com/wlsgur073/Guardians-of-the-Claude/issues/new) with the `[Security]` prefix in the title
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
