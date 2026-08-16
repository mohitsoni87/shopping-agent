from dataclasses import dataclass

# Prototype-stage trust boundary: tenant identity is read directly from these
# request headers, set by the edge/gateway. It is never derived from LLM output
# or request body. Production hardening (JWT/API-key resolution at the gateway)
# is a known, explicitly deferred gap - see design notes.
TENANT_ID_HEADER = "x-tenant-id"
ENV_HEADER = "x-env"


@dataclass(frozen=True, slots=True)
class TenantContext:
    tenant_id: str
    env: str
