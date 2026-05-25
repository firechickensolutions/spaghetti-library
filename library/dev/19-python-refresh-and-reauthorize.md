# Refresh and Reauthorize

**Language(s):** Python

**Rework-prevention rationale:** Prevents the AI generation failure mode where automation code obtains an access token once and assumes it remains valid for the whole run, ignoring expiry, refresh failure, rotated tokens, or mid-run revocation.

**Canonical source:** Aaron Parecki, *OAuth 2.0 Simplified*, "Refresh Tokens" (oauth.com/oauth2-servers/making-authenticated-requests/refreshing-an-access-token/); T. Lodderstedt, J. Bradley, A. Labunets, and D. Fett, *RFC 9700: Best Current Practice for OAuth 2.0 Security*, Section 4.14.2, "Recommendations."

## Trigger condition

Halt and read this entry when generated automation code obtains an access token once and then performs multiple API calls without checking token expiry before use, handling mid-run `401` or `invalid_token`, making one refresh-and-retry attempt, persisting any rotated token, and failing hard with reauthorization required when refresh fails.

## Before

```python
from requests_oauthlib import OAuth2Session

def run_job(oauth: OAuth2Session) -> None:
    token = oauth.fetch_token(TOKEN_URL)
    for item in load_items():
        oauth.post(ITEMS_URL, json=item,
                   headers={"Authorization": f"Bearer {token['access_token']}"})
```

## After

```python
from oauthlib.oauth2 import InvalidGrantError
from requests import HTTPError
from requests_oauthlib import OAuth2Session

class ReauthRequired(RuntimeError): pass

def post_with_refresh(api: OAuth2Session, store, url: str, item: dict):
    for attempt in (1, 2):
        try:
            r = api.post(url, json=item); r.raise_for_status(); return r
        except HTTPError as e:
            if e.response.status_code != 401 or attempt == 2: raise
            try: store.save(api.refresh_token(TOKEN_URL, **REFRESH_KWARGS))
            except InvalidGrantError as x: raise ReauthRequired("reauthorize") from x
```

**Pattern:** One retry loop: first `401` triggers refresh; if refresh raises `InvalidGrantError` (token revoked or expired), surface `ReauthRequired` to the caller. `store.save()` persists any rotated refresh token. `TOKEN_URL` and `REFRESH_KWARGS` are caller-configured at the composition root.
