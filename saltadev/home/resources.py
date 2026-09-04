"""Public grouping of admin-managed courses and tips."""

from collections.abc import Sequence
from dataclasses import dataclass

from content.models import LearningResource


@dataclass(frozen=True)
class TrackMeta:
    """Fixed copy and icon for a public resource track."""

    slug: str
    label: str
    blurb: str
    icon: str


@dataclass(frozen=True)
class ResourceTrack:
    """A track plus the published resources an administrator loaded."""

    slug: str
    label: str
    blurb: str
    icon: str
    resources: Sequence[LearningResource]


TRACKS = (
    TrackMeta(
        slug=LearningResource.Track.DEVELOPERS,
        label="Developers",
        blurb="Lenguajes, frameworks, control de versiones y markup.",
        icon="code",
    ),
    TrackMeta(
        slug=LearningResource.Track.VIBECODERS,
        label="Vibecoders",
        blurb="Uso de agentes de IA: contexto, revisión de cambios y manejo de secretos.",
        icon="auto_awesome",
    ),
)


def tracks_for_page() -> list[ResourceTrack]:
    """Return tracks that currently have at least one published approved course."""
    published = list(
        LearningResource.objects.filter(
            is_published=True,
            status=LearningResource.Status.APPROVED,
        ).order_by("order", "created_at", "pk")
    )
    grouped: dict[str, list[LearningResource]] = {}
    for resource in published:
        grouped.setdefault(resource.track, []).append(resource)
    return [
        ResourceTrack(
            slug=meta.slug,
            label=meta.label,
            blurb=meta.blurb,
            icon=meta.icon,
            resources=grouped[meta.slug],
        )
        for meta in TRACKS
        if grouped.get(meta.slug)
    ]
