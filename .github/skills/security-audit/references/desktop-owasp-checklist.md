# Desktop Application OWASP Checklist

Adapted from OWASP Top 10 for Python/PySide6 desktop applications with local file access, network APIs, and licensing systems.

---

## 1. Input Validation & Sanitization

### What to Check
- [ ] All user-provided text fields validated (email format, length limits, character restrictions)
- [ ] File paths from dialogs verified to exist and be within expected directories
- [ ] JSON/XML parsing uses safe parsers with size limits
- [ ] No `eval()`, `exec()`, or `compile()` on user input
- [ ] Filenames sanitized before filesystem operations (strip `..`, null bytes, OS-reserved chars)
- [ ] URL inputs validated against allowlist of schemes (`https://` only)
- [ ] Integer inputs bounded (prevent overflow in progress bars, batch sizes)

### How to Search
```
grep -rn "eval\|exec\|compile\|__import__" src/
grep -rn "input()\|QLineEdit\|text()" src/
grep -rn "\.format\|f'" src/ | grep -i "sql\|query\|command"
```

### Severity Guide
| Finding | Severity |
|---------|----------|
| `eval()` on user input | CRITICAL |
| No filename sanitization | HIGH |
| Missing email validation | MEDIUM |
| No length limits on text fields | LOW |

---

## 2. Secrets & Sensitive Data

### What to Check
- [ ] No hardcoded API keys, tokens, passwords, or license keys in source
- [ ] Session tokens encrypted at rest or stored in OS keychain
- [ ] License data file has restricted permissions (0o600)
- [ ] Credentials never appear in URLs (query parameters)
- [ ] `.gitignore` excludes config files with secrets
- [ ] No secrets in error messages, logs, or crash reports
- [ ] Clipboard cleared after copying sensitive data

### How to Search
```
grep -rn "password\|secret\|token\|api_key\|apikey" src/ --include="*.py"
grep -rn "hardcoded\|TODO.*secret" src/
find ~/.snapchat-organizer -name "*.json" -exec stat -f "%Lp %N" {} \;
```

### Severity Guide
| Finding | Severity |
|---------|----------|
| Hardcoded API key in source | CRITICAL |
| Plaintext token on disk without file permissions | HIGH |
| License key in URL query parameter | HIGH |
| Secrets in debug logs | MEDIUM |

---

## 3. Authentication & Authorization

### What to Check
- [ ] Passwords hashed with strong KDF (bcrypt, argon2, PBKDF2 ≥100k iterations)
- [ ] Salts are unique per user and cryptographically random
- [ ] Tokens generated with `secrets` module or `crypto.getRandomValues()`
- [ ] Session tokens have expiry and are validated server-side
- [ ] Failed login attempts rate-limited (server-side)
- [ ] Password reset flow doesn't leak user existence
- [ ] Device fingerprinting resistant to trivial spoofing

### Severity Guide
| Finding | Severity |
|---------|----------|
| Weak password hashing (MD5, SHA1, < 10k iterations) | CRITICAL |
| No token expiry | HIGH |
| No rate limiting on auth endpoints | HIGH |
| Missing password strength validation | MEDIUM |

---

## 4. Network Security

### What to Check
- [ ] All API calls use HTTPS (no plaintext HTTP)
- [ ] SSL certificate verification enabled (`verify=True` or default)
- [ ] Request timeouts set on all network calls
- [ ] CORS policy restricted to known origins (not `*`)
- [ ] Response data validated before use (check content-type, expected schema)
- [ ] No SSRF: user-provided URLs validated against allowlist
- [ ] Webhook signatures verified (Stripe, etc.)
- [ ] API versioning to prevent breaking changes

### How to Search
```
grep -rn "http://" src/ --include="*.py"
grep -rn "verify=False\|verify = False" src/
grep -rn "timeout" src/ --include="*.py"
grep -rn "Access-Control-Allow-Origin" worker/
```

### Severity Guide
| Finding | Severity |
|---------|----------|
| SSL verification disabled | CRITICAL |
| Plaintext HTTP for sensitive data | CRITICAL |
| CORS `*` with authenticated endpoints | HIGH |
| No request timeout | MEDIUM |

---

## 5. File I/O Safety

### What to Check
- [ ] No path traversal: user paths resolved with `Path.resolve()` and checked against base
- [ ] Symlink-safe: use `Path.resolve()` before operations to follow symlinks
- [ ] Temp files use `tempfile.TemporaryDirectory()` or `tempfile.NamedTemporaryFile()`
- [ ] File operations wrapped in try/except for permission errors
- [ ] `shutil.rmtree()` not called on user-provided paths without validation
- [ ] Created files have appropriate permissions (sensitive = 0o600)
- [ ] Large file operations stream instead of loading into memory
- [ ] No race conditions (TOCTOU) between check and use

### How to Search
```
grep -rn "open(\|Path(\|shutil\.\|os.remove\|os.unlink" src/
grep -rn "rmtree\|rmdir" src/
grep -rn "tempfile\|tmp\|temp" src/
```

### Severity Guide
| Finding | Severity |
|---------|----------|
| Path traversal possible | CRITICAL |
| `rmtree` on unvalidated path | HIGH |
| No temp file cleanup | MEDIUM |
| Default permissions on sensitive files | MEDIUM |

---

## 6. Subprocess & Command Execution

### What to Check
- [ ] No `shell=True` in `subprocess.run()` / `Popen()`
- [ ] Commands passed as lists, not strings
- [ ] No user input concatenated into commands
- [ ] Timeout set on all subprocess calls
- [ ] Return codes checked
- [ ] `stdout`/`stderr` captured (not mixed with app output)

### How to Search
```
grep -rn "subprocess\|Popen\|os.system\|os.popen" src/
grep -rn "shell=True" src/
```

### Severity Guide
| Finding | Severity |
|---------|----------|
| `shell=True` with user input | CRITICAL |
| `os.system()` used | HIGH |
| No timeout on subprocess | MEDIUM |
| Return code unchecked | LOW |

---

## 7. Dependency Security

### What to Check
- [ ] All dependencies pinned to specific versions in `requirements.txt`
- [ ] Run `pip audit` or `safety check` to find known CVEs
- [ ] No dependencies from untrusted sources
- [ ] Dev dependencies separated from production
- [ ] Lock file used (`pip-tools`, `poetry.lock`)
- [ ] Worker dependencies (`package.json`) audited with `npm audit`

### How to Check
```bash
pip install pip-audit && pip-audit -r requirements.txt
cd worker && npm audit
```

### Severity Guide
| Finding | Severity |
|---------|----------|
| Known CRITICAL CVE in dependency | CRITICAL |
| Unpinned dependency allowing malicious version | HIGH |
| Outdated dependency without known CVE | LOW |

---

## 8. Logging & Information Disclosure

### What to Check
- [ ] No passwords, tokens, or API keys in log output
- [ ] No PII (email, names, phone) in logs at INFO level or above
- [ ] Error messages to users are generic (no stack traces, internal paths)
- [ ] Log files have restricted permissions
- [ ] Log rotation configured (prevent disk exhaustion)
- [ ] Debug logging disabled in production builds
- [ ] Exception handlers don't expose internal state

### How to Search
```
grep -rn "logger\.\|logging\.\|\.error\|\.warning\|\.info\|\.debug" src/
grep -rn "traceback\|exc_info\|print(" src/
```

### Severity Guide
| Finding | Severity |
|---------|----------|
| Passwords/tokens logged | CRITICAL |
| Stack traces shown to user | MEDIUM |
| PII in info-level logs | MEDIUM |
| No log rotation | LOW |

---

## 9. Data Integrity

### What to Check
- [ ] Downloaded files verified with checksums (SHA-256)
- [ ] Database transactions used for multi-step operations
- [ ] File copy operations verified (compare size or hash after copy)
- [ ] JSON config files validated on load (handle corruption gracefully)
- [ ] Atomic file writes (write to temp, then rename) for critical data

### Severity Guide
| Finding | Severity |
|---------|----------|
| Downloaded executable not hash-verified | CRITICAL |
| No transaction around multi-row DB updates | HIGH |
| Config corruption causes crash | MEDIUM |

---

## 10. Desktop-Specific Threats

### What to Check
- [ ] App directory permissions restrict other users (`0o700`)
- [ ] No world-readable IPC sockets or named pipes
- [ ] Auto-update downloads verified before execution
- [ ] License validation has server-side enforcement (not just client-side)
- [ ] Sensitive memory cleared after use (limited in Python — note GC behavior)
- [ ] No DLL/dylib hijacking risk (use absolute paths for shared libraries)
- [ ] Drag-and-drop / clipboard input validated same as typed input

### Severity Guide
| Finding | Severity |
|---------|----------|
| Auto-update without signature verification | CRITICAL |
| Client-only license check (trivially bypassable) | HIGH |
| World-readable app data directory | MEDIUM |
