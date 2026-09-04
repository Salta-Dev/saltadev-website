"""Public queries for books, tools and community projects."""

from typing import TYPE_CHECKING

from content.models import CatalogEntry
from django.utils import timezone
from users.models import User

if TYPE_CHECKING:
    from django.forms import ModelForm


def entries_for_kind(kind: str) -> list[CatalogEntry]:
    """Return published, approved catalog entries for one Recursos tab."""
    return list(
        CatalogEntry.objects.filter(
            kind=kind,
            is_published=True,
            status=CatalogEntry.Status.APPROVED,
        ).order_by("order", "title", "pk")
    )


def can_approve_catalog(user: User) -> bool:
    """Return True for Django superusers or SaltaDev administrators."""
    return bool(
        user.is_superuser or (user.is_staff and user.role == User.Role.ADMINISTRADOR)
    )


def submit_catalog_entry(form: "ModelForm", user: User, kind: str) -> CatalogEntry:
    """Persist a catalog row, pending unless an administrator submits it."""
    entry = form.save(commit=False)
    entry.kind = kind
    entry.creator = user
    if kind == CatalogEntry.Kind.PROJECT and not entry.authors:
        full_name = f"{user.first_name} {user.last_name}".strip()
        entry.authors = full_name or user.email
    if can_approve_catalog(user):
        entry.status = CatalogEntry.Status.APPROVED
        entry.is_published = True
        entry.approved_by = user
        entry.approved_at = timezone.now()
    else:
        entry.status = CatalogEntry.Status.PENDING
        entry.is_published = False
    entry.save()
    return entry
