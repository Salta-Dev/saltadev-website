"""Proposals lifecycle for Recursos (catalog entries and courses)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import urlparse, urlunparse

from content.models import CatalogEntry, LearningResource
from django.urls import reverse
from django.utils import timezone
from notifications.signals import notify
from users.models import User

if TYPE_CHECKING:
    from django.forms import ModelForm

KIND_LABELS: dict[str, str] = {
    str(CatalogEntry.Kind.READING): "Lectura",
    str(CatalogEntry.Kind.TOOL): "Herramienta",
    str(CatalogEntry.Kind.PROJECT): "Proyecto",
    "course": "Curso",
}


@dataclass(frozen=True)
class ProposalRow:
    """One row in Mis propuestas or the review queue."""

    object_type: str
    pk: int
    kind_label: str
    title: str
    summary: str
    url: str
    status: str
    status_label: str
    creator_label: str
    created_at: datetime
    rejection_reason: str
    public_url_name: str


def normalize_canonical_url(url: str) -> str:
    """Normalize a resource URL for duplicate detection."""
    raw = (url or "").strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    scheme = (parsed.scheme or "https").casefold()
    netloc = parsed.netloc.casefold()
    path = parsed.path.rstrip("/")
    return urlunparse((scheme, netloc, path, "", "", ""))


def can_review_recursos(user: User) -> bool:
    """Return True for administrators and moderators (and superusers)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.role in {User.Role.ADMINISTRADOR, User.Role.MODERADOR}


def can_submit_propuestas(user: User) -> bool:
    """Return True for logged-in members with a verified email."""
    return bool(user.is_authenticated and user.email_confirmed)


def can_approve_catalog(user: User) -> bool:
    """Alias kept for older call sites; Revisores may auto-publish."""
    return can_review_recursos(user)


def entries_for_kind(kind: str) -> list[CatalogEntry]:
    """Return published, approved catalog entries for one Recursos tab."""
    return list(
        CatalogEntry.objects.filter(
            kind=kind,
            is_published=True,
            status=CatalogEntry.Status.APPROVED,
        ).order_by("order", "title", "pk")
    )


def hub_url_is_taken(url: str, *, exclude_catalog_pk: int | None = None) -> bool:
    """Return True when an approved or pending hub Recurso already uses this URL."""
    canonical = normalize_canonical_url(url)
    if not canonical:
        return False

    catalog_qs = CatalogEntry.objects.filter(
        status__in={CatalogEntry.Status.APPROVED, CatalogEntry.Status.PENDING},
    ).exclude(url="")
    if exclude_catalog_pk is not None:
        catalog_qs = catalog_qs.exclude(pk=exclude_catalog_pk)
    for entry in catalog_qs.only("url"):
        if normalize_canonical_url(entry.url) == canonical:
            return True

    course_qs = LearningResource.objects.filter(
        status__in={
            LearningResource.Status.APPROVED,
            LearningResource.Status.PENDING,
        },
    ).exclude(url="")
    for course in course_qs.only("url"):
        if normalize_canonical_url(course.url) == canonical:
            return True
    return False


def submit_catalog_entry(form: ModelForm, user: User, kind: str) -> CatalogEntry:
    """Persist a catalog row, pending unless a Revisor submits it."""
    entry = form.save(commit=False)
    entry.kind = kind
    entry.creator = user
    if kind == CatalogEntry.Kind.PROJECT and not entry.authors:
        full_name = f"{user.first_name} {user.last_name}".strip()
        entry.authors = full_name or user.email
    if can_review_recursos(user):
        entry.status = CatalogEntry.Status.APPROVED
        entry.is_published = True
        entry.approved_by = user
        entry.approved_at = timezone.now()
        entry.rejection_reason = ""
    else:
        entry.status = CatalogEntry.Status.PENDING
        entry.is_published = False
        entry.rejection_reason = ""
    entry.save()
    return entry


def submit_course(form: ModelForm, user: User) -> LearningResource:
    """Persist a course proposal, pending unless a Revisor submits it."""
    course = form.save(commit=False)
    course.creator = user
    if can_review_recursos(user):
        course.status = LearningResource.Status.APPROVED
        course.is_published = True
        course.approved_by = user
        course.approved_at = timezone.now()
        course.rejection_reason = ""
    else:
        course.status = LearningResource.Status.PENDING
        course.is_published = False
        course.rejection_reason = ""
    course.save()
    return course


def _creator_label(user: User | None) -> str:
    if user is None:
        return "—"
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.email


def _catalog_public_url_name(kind: str) -> str:
    """Map a catalog kind to its public Recursos URL name."""
    mapping: dict[str, str] = {
        str(CatalogEntry.Kind.READING): "resource_reading",
        str(CatalogEntry.Kind.TOOL): "resource_tools",
        str(CatalogEntry.Kind.PROJECT): "resource_projects",
    }
    return mapping.get(str(kind), "resources")


def _catalog_row(entry: CatalogEntry) -> ProposalRow:
    return ProposalRow(
        object_type="catalog",
        pk=entry.pk,
        kind_label=KIND_LABELS.get(str(entry.kind), str(entry.kind)),
        title=entry.title,
        summary=entry.summary,
        url=entry.url,
        status=entry.status,
        status_label=entry.get_status_display(),
        creator_label=_creator_label(entry.creator),
        created_at=entry.created_at,
        rejection_reason=entry.rejection_reason,
        public_url_name=_catalog_public_url_name(entry.kind),
    )


def _course_row(course: LearningResource) -> ProposalRow:
    return ProposalRow(
        object_type="course",
        pk=course.pk,
        kind_label=KIND_LABELS["course"],
        title=course.title,
        summary=course.tip,
        url=course.url,
        status=course.status,
        status_label=course.get_status_display(),
        creator_label=_creator_label(course.creator),
        created_at=course.created_at,
        rejection_reason=course.rejection_reason,
        public_url_name="resources",
    )


def proposals_for_member(user: User) -> list[ProposalRow]:
    """Return the member's catalog and course proposals, newest first."""
    rows = [_catalog_row(entry) for entry in CatalogEntry.objects.filter(creator=user)]
    rows.extend(
        _course_row(course) for course in LearningResource.objects.filter(creator=user)
    )
    rows.sort(key=lambda row: row.created_at, reverse=True)
    return rows


def pending_proposals() -> list[ProposalRow]:
    """Return all pending hub proposals for reviewers."""
    rows = [
        _catalog_row(entry)
        for entry in CatalogEntry.objects.filter(status=CatalogEntry.Status.PENDING)
        .select_related("creator")
        .order_by("-created_at")
    ]
    rows.extend(
        _course_row(course)
        for course in LearningResource.objects.filter(
            status=LearningResource.Status.PENDING
        )
        .select_related("creator")
        .order_by("-created_at")
    )
    rows.sort(key=lambda row: row.created_at, reverse=True)
    return rows


def notify_proposal_decision(
    *,
    actor: CatalogEntry | LearningResource,
    recipient: User,
    title: str,
    approved: bool,
    reason: str = "",
) -> None:
    """Send an in-app notification to the Miembro about Publicación or Rechazo."""
    if approved:
        verb = "Propuesta publicada"
        description = f'Tu propuesta "{title}" ya está en Recursos.'
    else:
        verb = "Propuesta rechazada"
        description = f'Tu propuesta "{title}" fue rechazada.'
        if reason:
            description = f"{description} Motivo: {reason}"
    notify.send(
        sender=actor,
        recipient=recipient,
        verb=verb,
        description=description,
        url=reverse("my_resource_proposals"),
    )


def approve_catalog_entry(entry: CatalogEntry, reviewer: User) -> None:
    """Publish a catalog proposal and notify the creator."""
    entry.approve(reviewer)
    if entry.creator_id and entry.creator_id != reviewer.pk and entry.creator:
        notify_proposal_decision(
            actor=entry,
            recipient=entry.creator,
            title=entry.title,
            approved=True,
        )


def reject_catalog_entry(entry: CatalogEntry, reviewer: User, reason: str = "") -> None:
    """Reject a catalog proposal and notify the creator."""
    entry.reject(reviewer, reason=reason)
    if entry.creator_id and entry.creator_id != reviewer.pk and entry.creator:
        notify_proposal_decision(
            actor=entry,
            recipient=entry.creator,
            title=entry.title,
            approved=False,
            reason=reason,
        )


def approve_course(course: LearningResource, reviewer: User) -> None:
    """Publish a course proposal and notify the creator."""
    course.approve(reviewer)
    if course.creator_id and course.creator_id != reviewer.pk and course.creator:
        notify_proposal_decision(
            actor=course,
            recipient=course.creator,
            title=course.title,
            approved=True,
        )


def reject_course(course: LearningResource, reviewer: User, reason: str = "") -> None:
    """Reject a course proposal and notify the creator."""
    course.reject(reviewer, reason=reason)
    if course.creator_id and course.creator_id != reviewer.pk and course.creator:
        notify_proposal_decision(
            actor=course,
            recipient=course.creator,
            title=course.title,
            approved=False,
            reason=reason,
        )
