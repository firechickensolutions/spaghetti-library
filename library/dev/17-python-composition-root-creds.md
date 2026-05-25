# Composition Root Credentials

**Language(s):** Python

**Rework-prevention rationale:** Prevents the AI generation failure mode where credentials are hardcoded or held in module globals instead of being read at the composition root and injected into the adapter or function that needs them.

**Canonical source:** Adam Wiggins, *The Twelve-Factor App*, "III. Config" (12factor.net/config); OWASP Foundation, *Secure Coding Practices Quick Reference Guide*, "Authentication and Password Management."

## Trigger condition

Halt and read this entry when generated code places an API key, token, client secret, password, or credential-bearing config object in a function body, module global, checked-in config dictionary, or reusable domain function instead of constructing it once at the composition root and passing it in.

## Before

```python
import requests

API = {"base_url": "https://api.vendor.test", "token": "sk_live_123"}

def sync_customer(customer_id: str) -> None:
    requests.post(f"{API['base_url']}/customers/{customer_id}/sync",
                  headers={"Authorization": f"Bearer {API['token']}"})
```

## After

```python
import os
import requests
from dataclasses import dataclass

@dataclass(frozen=True)
class ApiCreds:
    base_url: str
    token: str

# composition root: read from environment once, inject everywhere
creds = ApiCreds(os.environ["VENDOR_BASE_URL"], os.environ["VENDOR_TOKEN"])

def sync_customer(customer_id: str, creds: ApiCreds) -> None:
    requests.post(f"{creds.base_url}/customers/{customer_id}/sync",
                  headers={"Authorization": f"Bearer {creds.token}"})
```

**Pattern:** Twelve-Factor III covers *where creds originate* (environment, not code). Dependency injection covers *how they reach the function* (parameter, not global). Both are needed: `os.environ` read at the composition root, credential object constructed once, passed into every function that needs it.
