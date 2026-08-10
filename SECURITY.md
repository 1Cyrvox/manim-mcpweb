# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in manim-web, **please do not open a public GitHub Issue**.

Instead, please report it privately by:

1. **GitHub Security Advisory** (preferred): Go to [Security → Advisories](https://github.com/1Cyrvox/manim-mcpweb/security/advisories) and submit a new advisory.

2. **GitHub Issue with `security` label**: If you cannot use the advisory feature, open an issue and label it `security`, providing only a high-level description without exploit details.

## What to Include

- Description of the vulnerability
- Affected version(s)
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (optional)

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 7 days
- **Fix or mitigation**: Depends on severity
  - Critical (RCE, data leak): Within 72 hours
  - High (sandbox escape): Within 7 days
  - Medium/Low: Next release cycle

## Scope

### In Scope

- Sandbox escape vulnerabilities (code execution bypass in strict/relaxed mode)
- Authentication or authorization bypass
- Remote code execution via MCP protocol
- Path traversal in project store
- WebSocket security issues

### Out of Scope

- Issues in upstream manim (report to [manimcommunity/manim](https://github.com/manimcommunity/manim))
- Denial of service via resource exhaustion (mitigated by sandbox)
- Social engineering attacks

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.0.x   | Yes       |
| < 2.0   | No        |