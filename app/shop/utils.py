from typing import Any

#This is for logging so we can see what users are doing on the UI side. 

def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def create_audit_log(request, action: str, details: str = "", target_type: str = "", target_id: Any = "", user=None ) -> None:
    from .models import AuditLog

    actor = user if user is not None else getattr(request, "user", None)

    is_authenticated = bool(actor and getattr(actor, "is_authenticated", False))

    AuditLog.objects.create(
        user=actor if is_authenticated else None,
        username_snapshot=getattr(actor, "username", "") if actor else "",
        role_snapshot=getattr(actor, "role", "") if actor else "",
        action=action,
        details=details,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        path=request.path,
        method=request.method,
        target_type=target_type,
        target_id=str(target_id) if target_id != "" else "",
    )