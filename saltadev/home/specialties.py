"""Public grouping of admin-managed IT specialties."""

from collections.abc import Sequence
from dataclasses import dataclass

from content.models import TechSpecialty


@dataclass(frozen=True)
class FamilyMeta:
    """Fixed copy for a public specialty family."""

    slug: str
    label: str
    blurb: str


@dataclass(frozen=True)
class SpecialtyFamily:
    """A family plus the published roles an administrator loaded."""

    slug: str
    label: str
    blurb: str
    specialties: Sequence[TechSpecialty]


FAMILIES = (
    FamilyMeta(
        slug=TechSpecialty.Family.DEVELOPMENT,
        label="Desarrollo",
        blurb="Roles que construyen el producto: web, mobile, juegos y blockchain.",
    ),
    FamilyMeta(
        slug=TechSpecialty.Family.DATA,
        label="Datos e IA",
        blurb="Del dato crudo al análisis y a los modelos en producción.",
    ),
    FamilyMeta(
        slug=TechSpecialty.Family.OPERATIONS,
        label="Operaciones y calidad",
        blurb="Infraestructura, seguridad, testing y que el sistema se sostenga.",
    ),
    FamilyMeta(
        slug=TechSpecialty.Family.DESIGN,
        label="Diseño",
        blurb="La interfaz y el recorrido de quien usa el producto.",
    ),
    FamilyMeta(
        slug=TechSpecialty.Family.PRODUCT,
        label="Producto",
        blurb="Qué se construye, para quién y cuándo se entrega.",
    ),
    FamilyMeta(
        slug=TechSpecialty.Family.LEADERSHIP,
        label="Liderazgo",
        blurb="Decisiones técnicas y de equipo cuando el sistema crece.",
    ),
)


def specialties_for_page() -> list[SpecialtyFamily]:
    """Return families that currently have at least one published specialty."""
    published = list(
        TechSpecialty.objects.filter(is_published=True).order_by("order", "title", "pk")
    )
    grouped: dict[str, list[TechSpecialty]] = {}
    for specialty in published:
        grouped.setdefault(specialty.family, []).append(specialty)
    return [
        SpecialtyFamily(
            slug=meta.slug,
            label=meta.label,
            blurb=meta.blurb,
            specialties=grouped[meta.slug],
        )
        for meta in FAMILIES
        if grouped.get(meta.slug)
    ]
