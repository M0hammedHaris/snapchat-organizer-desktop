# Remediation Patterns

Battle-tested code patterns for fixing common security findings in Python desktop applications.

---

## Encrypt Secrets at Rest (OS Keychain)

**Fixes**: Plaintext tokens/license data on disk

### macOS — Keychain via `keyring`
```python
import keyring

SERVICE_NAME = "com.snapchat-organizer.desktop"

def store_token(user_email: str, token: str) -> None:
    """Store session token in OS keychain."""
    keyring.set_password(SERVICE_NAME, user_email, token)

def get_token(user_email: str) -> str | None:
    """Retrieve session token from OS keychain."""
    return keyring.get_password(SERVICE_NAME, user_email)

def delete_token(user_email: str) -> None:
    """Remove session token from OS keychain."""
    try:
        keyring.delete_password(SERVICE_NAME, user_email)
    except keyring.errors.PasswordDeleteError:
        pass
```

### Fallback — File encryption with restricted permissions
```python
import os
import json
from pathlib import Path
from cryptography.fernet import Fernet

def save_sensitive_file(path: Path, data: dict, key: bytes) -> None:
    """Save encrypted data with restricted file permissions."""
    f = Fernet(key)
    encrypted = f.encrypt(json.dumps(data).encode())
    path.write_bytes(encrypted)
    os.chmod(path, 0o600)  # Owner read/write only

def load_sensitive_file(path: Path, key: bytes) -> dict | None:
    """Load and decrypt sensitive data."""
    if not path.exists():
        return None
    f = Fernet(key)
    decrypted = f.decrypt(path.read_bytes())
    return json.loads(decrypted.decode())
```

---

## Restrict File Permissions

**Fixes**: Default umask on sensitive files (config, license data, logs)

```python
import os
from pathlib import Path

def create_secure_directory(path: Path) -> None:
    """Create directory with owner-only access."""
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)

def write_secure_file(path: Path, content: str) -> None:
    """Write file with owner-only read/write."""
    path.write_text(content, encoding="utf-8")
    os.chmod(path, 0o600)
```

---

## Email Validation

**Fixes**: Missing email format validation on login/register forms

```python
import re

EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

def is_valid_email(email: str) -> bool:
    """Validate email format. Not exhaustive — server validates authoritatively."""
    if not email or len(email) > 254:
        return False
    return EMAIL_PATTERN.match(email) is not None
```

### PySide6 integration
```python
from PySide6.QtWidgets import QLineEdit, QLabel

def validate_email_field(email_input: QLineEdit, error_label: QLabel) -> bool:
    """Validate email and show inline error."""
    email = email_input.text().strip()
    if not is_valid_email(email):
        error_label.setText("Please enter a valid email address")
        error_label.setStyleSheet("color: red;")
        return False
    error_label.clear()
    return True
```

---

## Safe Temp Directory Handling

**Fixes**: Temp directories not created via `tempfile`, cleanup not guaranteed

```python
import tempfile
from pathlib import Path

# Context manager — auto-cleanup guaranteed
def process_with_temp():
    with tempfile.TemporaryDirectory(prefix="snaporg_") as tmp:
        tmp_path = Path(tmp)
        # Use tmp_path for intermediate files
        # Auto-deleted when context exits, even on exception
```

---

## Secure Subprocess Execution

**Fixes**: Shell injection, missing timeouts, unchecked return codes

```python
import subprocess
import logging

logger = logging.getLogger(__name__)

def run_command(
    args: list[str],
    timeout: int = 10
) -> str | None:
    """Run external command safely."""
    try:
        result = subprocess.run(
            args,                    # List form — no shell injection
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,             # Explicit — never use shell=True
        )
        if result.returncode != 0:
            logger.warning(
                "Command %s exited with code %d: %s",
                args[0], result.returncode, result.stderr[:200]
            )
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error("Command %s timed out after %ds", args[0], timeout)
        return None
    except FileNotFoundError:
        logger.error("Command not found: %s", args[0])
        return None
```

---

## URL Validation (Prevent SSRF / Unsafe Opens)

**Fixes**: Opening arbitrary URLs via subprocess, license keys in URLs

```python
from urllib.parse import urlparse
import webbrowser

ALLOWED_HOSTS = {
    "snapchat-organizer.com",
    "www.snapchat-organizer.com",
}

def open_safe_url(url: str) -> bool:
    """Open URL in browser after validating host and scheme."""
    parsed = urlparse(url)
    if parsed.scheme not in ("https",):
        return False
    if parsed.hostname not in ALLOWED_HOSTS:
        return False
    # Use webbrowser module — cross-platform, no subprocess needed
    webbrowser.open(url)
    return True
```

---

## Rate Limiting (Server-Side)

**Fixes**: No brute-force protection on auth endpoints

### Cloudflare Worker pattern (D1)
```javascript
async function checkRateLimit(env, ip, endpoint, maxAttempts = 5, windowSecs = 300) {
  const key = `${ip}:${endpoint}`;
  const windowStart = Math.floor(Date.now() / 1000) - windowSecs;

  // Count recent attempts
  const { results } = await env.DB.prepare(
    'SELECT COUNT(*) as count FROM rate_limits WHERE key = ? AND timestamp > ?'
  ).bind(key, windowStart).all();

  if (results[0].count >= maxAttempts) {
    return { allowed: false, retryAfter: windowSecs };
  }

  // Record attempt
  await env.DB.prepare(
    'INSERT INTO rate_limits (key, timestamp) VALUES (?, ?)'
  ).bind(key, Math.floor(Date.now() / 1000)).run();

  return { allowed: true };
}
```

---

## Restrict CORS

**Fixes**: `Access-Control-Allow-Origin: *` on authenticated endpoints

```javascript
// worker/src/utils/response.js
const ALLOWED_ORIGINS = [
  'https://snapchat-organizer.com',
  'https://www.snapchat-organizer.com',
];

function getCorsHeaders(request) {
  const origin = request.headers.get('Origin');
  // For desktop apps (no Origin header), allow the request
  // For web requests, check against allowlist
  const allowOrigin = (!origin || ALLOWED_ORIGINS.includes(origin))
    ? (origin || '*')
    : null;

  if (!allowOrigin) return null; // Block

  return {
    'Access-Control-Allow-Origin': allowOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  };
}
```

---

## Atomic File Writes

**Fixes**: Config/data corruption on crash during write

```python
import os
import json
import tempfile
from pathlib import Path

def atomic_json_write(path: Path, data: dict) -> None:
    """Write JSON atomically — either fully written or not at all."""
    dir_path = path.parent
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=dir_path,
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        json.dump(data, tmp, indent=2)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = tmp.name

    os.replace(tmp_path, path)  # Atomic on POSIX
```

---

## Safe URL Opening (No License Keys in URLs)

**Fixes**: Sensitive data in browser URLs / server logs

```python
# Instead of:
#   subprocess.Popen(['open', f'https://example.com/upgrade?key={key}'])
#
# Use a POST-based redirect or strip sensitive params:

def open_upgrade_page() -> None:
    """Open upgrade page without leaking license key."""
    webbrowser.open("https://snapchat-organizer.com/upgrade")
    # User authenticates on the website separately
```

---

## Dependency Audit Script

**Fixes**: Unknown CVEs in dependencies

```bash
#!/usr/bin/env bash
# scripts/security_check.sh
set -euo pipefail

echo "=== Python Dependency Audit ==="
pip-audit -r requirements.txt --strict 2>&1 || echo "WARN: pip-audit found issues"

echo ""
echo "=== Node.js Dependency Audit ==="
(cd worker && npm audit --production) 2>&1 || echo "WARN: npm audit found issues"

echo ""
echo "=== Hardcoded Secrets Scan ==="
grep -rn "password\s*=\s*['\"]" src/ --include="*.py" && echo "WARN: Potential hardcoded password" || echo "OK: No hardcoded passwords found"
grep -rn "secret\s*=\s*['\"]" src/ --include="*.py" && echo "WARN: Potential hardcoded secret" || echo "OK: No hardcoded secrets found"

echo ""
echo "=== Shell Injection Risk ==="
grep -rn "shell=True" src/ --include="*.py" && echo "WARN: shell=True found" || echo "OK: No shell=True usage"
grep -rn "os\.system\|os\.popen" src/ --include="*.py" && echo "WARN: os.system/popen found" || echo "OK: No os.system/popen usage"
```
