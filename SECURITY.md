# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, use one of the following methods:

1. **GitHub Security Advisories** (preferred): [Report a vulnerability](https://github.com/JaylenAI/Notion_Forge/security/advisories/new)
2. **Email**: Create a private security advisory on the repository

### What to include

- Type of vulnerability (e.g., XSS, injection, authentication bypass)
- Location of the affected source code (file path, line number)
- Step-by-step instructions to reproduce
- Impact assessment
- Suggested fix (if any)

### Response Timeline

| Action | Timeline |
|--------|----------|
| Acknowledge receipt | 72 hours |
| Initial assessment | 5 business days |
| Fix for CRITICAL | 7 days |
| Fix for HIGH | 14 days |
| Fix for MEDIUM/LOW | Next release |

## Security Measures

### Input Validation
- All user inputs validated via Pydantic models with strict type checking
- Prompt injection defense via `InputGuardrail` (pattern matching + heuristic analysis)
- Path traversal prevention on skill/file operations
- Regex-based Notion page ID validation

### API Security
- CORS configuration with explicit origin allowlist
- Request size limits on all endpoints
- Rate limiting middleware (configurable via `RATE_LIMIT_RPM`)
- Structured error responses (no stack trace leakage in production)

### Notion API
- Token validation before API calls
- Rate limiter with exponential backoff
- Automatic retry with circuit breaker pattern
- Token never logged or stored beyond session

### WebSocket
- Connection timeout (10s) for unauthenticated sessions
- Per-connection message rate limiting
- Graceful disconnection on invalid state

### Dependencies
- Automated dependency updates via Dependabot
- `pip-audit` in CI pipeline for known vulnerabilities
- Minimal dependency footprint

## Self-Hosted Security Recommendations

NotionForge is designed for self-hosted deployment. Operators should:

1. **Use HTTPS** in production (reverse proxy with TLS termination)
2. **Restrict network access** — do not expose the API to the public internet without authentication
3. **Rotate Notion tokens** periodically
4. **Set environment variables** securely (never commit `.env` files)
5. **Enable rate limiting** via `RATE_LIMIT_RPM` environment variable
6. **Monitor logs** for unusual activity patterns
7. **Keep dependencies updated** — run `uv lock --upgrade` regularly

## Environment Variables Security

| Variable | Sensitivity | Notes |
|----------|------------|-------|
| `NOTION_API_KEY` | HIGH | Never commit, rotate regularly |
| `ANTHROPIC_API_KEY` | HIGH | Never commit |
| `GEMINI_API_KEY` | HIGH | Never commit |
| `GROQ_API_KEY` | HIGH | Never commit |
| `NOTION_OAUTH_CLIENT_SECRET` | HIGH | Never commit |
| `NOTION_OAUTH_CLIENT_ID` | MEDIUM | Public in OAuth flow |
| `FRONTEND_URL` | LOW | Used for CORS/redirect |

## Known Limitations

- **No built-in authentication**: This is a self-hosted tool. Deploy behind a VPN or reverse proxy with auth (e.g., Cloudflare Access, OAuth2 Proxy, Authelia).
- **In-memory task store**: Task state is lost on process restart. Use Redis backend for persistence (`TASK_STORE=redis`).
- **Single-instance design**: Not designed for horizontal scaling without shared state backend.
