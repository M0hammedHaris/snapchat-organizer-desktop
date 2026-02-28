---
name: security-audit
description: "Security audit and hardening for Python desktop applications. USE FOR: finding vulnerabilities, fixing insecure code, improving application security standards, OWASP analysis, secrets handling, input validation, file I/O safety, network security, auth hardening, dependency scanning. Covers desktop-specific threats: path traversal, plaintext secrets, unsafe subprocess, permissive file permissions, license key leakage."
argument-hint: "Describe what to audit: full app, specific module, or category (e.g., 'auth system', 'file handling', 'network calls')"
---

# Security Audit & Hardening

Perform a structured security audit on the codebase, identify vulnerabilities, fix issues, and raise the application to production security standards.

## When to Use

- Before a release to verify security posture
- After adding new features involving auth, network, file I/O, or user input
- When integrating third-party libraries or APIs
- Periodic security review of the full codebase
- When a specific security concern is raised

## Audit Procedure

### Phase 1: Scope & Discovery

1. **Determine audit scope** from user request:
   - **Full audit**: All categories below, end-to-end
   - **Module audit**: Specific file or directory (e.g., `src/license/`)
   - **Category audit**: Single domain (e.g., "network security", "secrets handling")

2. **Gather context** — read the target files. Use a subagent for broad exploration:
   - Map all entry points (user input, file I/O, network, subprocess, config)
   - Identify sensitive data flows (tokens, passwords, license keys, PII)
   - List third-party dependencies and their versions

### Phase 2: Audit Checks

Run through each applicable category from the [Desktop OWASP Checklist](./references/desktop-owasp-checklist.md). For each finding:
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW / INFO
- **Location**: File path and line number
- **Description**: What's wrong and why it matters
- **Status**: VULNERABLE / SECURE / NEEDS IMPROVEMENT

Categories (run all for full audit, or pick per scope):

1. **Input Validation & Sanitization**
   - Form fields, file paths, URLs, JSON parsing
   - Email/password format validation
   - Path traversal prevention

2. **Secrets & Sensitive Data**
   - Plaintext tokens/keys on disk
   - Hardcoded secrets in source
   - Credentials in logs or URLs
   - File permissions on sensitive files

3. **Authentication & Authorization**
   - Password hashing strength
   - Token generation and storage
   - Session management and expiry
   - Rate limiting and brute-force protection

4. **Network Security**
   - TLS/SSL verification
   - CORS policy
   - Request timeouts
   - URL validation (SSRF prevention)
   - Certificate pinning considerations

5. **File I/O Safety**
   - Path traversal / directory escape
   - Symlink attacks
   - Temp file handling
   - File permission enforcement
   - Safe file copy/move patterns

6. **Subprocess & Command Execution**
   - Shell injection (shell=True, string commands)
   - Argument injection
   - Timeout enforcement
   - Untrusted data in command arguments

7. **Dependency Security**
   - Known CVEs in pinned versions
   - Unpinned or outdated dependencies
   - Supply chain risks

8. **Logging & Information Disclosure**
   - Sensitive data in logs (tokens, passwords, PII)
   - Verbose error messages exposed to users
   - Log file permissions and rotation
   - Stack traces in production

9. **Data Integrity**
   - Hash verification for downloads
   - File integrity checks
   - Database transaction safety

10. **Desktop-Specific Threats**
    - Local privilege escalation paths
    - IPC security (if applicable)
    - Auto-update mechanism safety
    - License bypass resistance

### Phase 3: Remediation

For each finding rated MEDIUM or above:

1. **Fix the vulnerability** directly in code — refer to [Remediation Patterns](./references/remediation-patterns.md) for battle-tested fixes
2. **Verify the fix** — re-check the finding after applying the change
3. **Document** what was changed and why (in commit message, not extra files)

Prioritization order:
1. CRITICAL — Fix immediately (data exposure, injection, auth bypass)
2. HIGH — Fix before release (weak crypto, missing validation, plaintext secrets)
3. MEDIUM — Fix soon (permissive CORS, info disclosure, missing rate limits)
4. LOW/INFO — Track for future improvement

### Phase 4: Report

After completing the audit, produce a summary:

```
## Security Audit Summary

**Scope**: [Full / Module / Category]
**Date**: [Date]
**Files Audited**: [count]

### Findings by Severity
| Severity | Found | Fixed | Remaining |
|----------|-------|-------|-----------|
| CRITICAL |       |       |           |
| HIGH     |       |       |           |
| MEDIUM   |       |       |           |
| LOW      |       |       |           |

### Key Changes Made
- [Brief list of fixes applied]

### Remaining Recommendations
- [Items that need manual review or architectural changes]
```

## Decision Points

- **Plaintext secrets on disk?** → Encrypt with OS keychain (macOS Keychain / Windows DPAPI) or at minimum restrict file permissions to 0o600
- **Shell=True in subprocess?** → Always use list arguments; never pass user data through shell
- **No input validation?** → Add validation at system boundaries only (user input, external API responses) — don't over-validate internal calls
- **Outdated dependency?** → Check if CVE affects the usage pattern before upgrading; pin to patched version
- **CORS wildcard?** → Restrict to known origins; for desktop apps with no web frontend, consider removing CORS entirely

## Quality Criteria

An audit is complete when:
- [ ] All categories in scope have been checked
- [ ] Every CRITICAL and HIGH finding has a fix or documented exception
- [ ] Fixes have been verified (re-read changed code)
- [ ] No new vulnerabilities introduced by fixes
- [ ] Summary report generated
