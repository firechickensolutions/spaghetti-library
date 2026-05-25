# Boundary Permission Gate

**Language(s):** Python

**Rework-prevention rationale:** Prevents the AI generation failure mode where authorization checks are scattered inside business logic instead of enforced once at the boundary where the call enters the trusted use case.

**Canonical source:** OWASP Foundation, *Secure Coding Practices Quick Reference Guide*, "Access Control"; OWASP Foundation, *Threat Modeling Process*, "Trust Levels" and "Entry Points"; Harry Percival and Bob Gregory, *Architecture Patterns with Python*, Chapter 4, "Our First Use Case: Flask API and Service Layer" (cosmicpython.com): architectural support for service-layer boundary, not the auth authority.

## Trigger condition

Halt and read this entry when generated code adds `if user.role`, `if permission`, `is_admin`, `require_scope`, or equivalent authorization logic inside a domain or business function instead of at the CLI command, HTTP handler, job runner, orchestrator step, or service-layer entrypoint.

## Before

```python
def approve_deploy(user: User, deploy_id: str) -> None:
    if "deploy:approve" not in user.permissions:
        raise PermissionError("not allowed")
    deploy = repo.get(deploy_id)
    deploy.approve(user.id)
    repo.save(deploy)
```

## After

```python
# boundary / entrypoint: permission decision lives here
def approve_deploy_endpoint(user: User, deploy_id: str) -> None:
    authorizer.require(user, "deploy:approve")
    approve_deploy(deploy_id, approved_by=user.id)

# domain use case: no permission logic; actor flows in as command data
def approve_deploy(deploy_id: str, approved_by: str) -> None:
    deploy = repo.get(deploy_id)
    deploy.approve(approved_by)
    repo.save(deploy)
```

**Rule:** The permission *decision* lives at the boundary. The actor identity (`approved_by`) still flows inward as business/audit data: do not drop it from the domain function.
