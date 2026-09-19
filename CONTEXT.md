# SaltaDev Website

Community site for SaltaDev (Salta, Argentina): events, member benefits, and a public Recursos hub.

## Language

### Recursos hub

**Recurso**:
An item the community can discover on the public Recursos hub. Includes books (Lectura), tools (Herramientas), community projects (Proyectos), and courses/tips (Cursos).
_Avoid_: Catalog row (implementation), LearningResource (implementation), generic "content"

**Propuesta**:
A Recurso submitted by a Miembro that awaits review before it appears publicly. Applies to Lectura, Herramientas, Proyectos, and Cursos, even when they live in different storage shapes.
_Avoid_: Draft, ticket, pending resource (as the public name)

**Publicación**:
The act of a Revisor accepting a Propuesta so the Recurso becomes visible on the hub.
_Avoid_: Publish toggle alone, Django admin approve (as the product name)

**Rechazo**:
The act of a Revisor declining a Propuesta. The record remains with status rejected and stays off the public hub.
_Avoid_: Delete (unless the entry is actually removed), unpublish

**Revisor**:
An Administrador or Moderador who can review Propuestas on the site (same roles that review Events).
_Avoid_: Staff member (broader), Django superuser (implementation detail), Administrador-only for Recursos

**Administrador**:
A SaltaDev staff user with the administrator role.
_Avoid_: Using this term alone when Moderador is also allowed to review

**Moderador**:
A SaltaDev staff user with the moderator role; may review Propuestas and Events alongside Administradores.
_Avoid_: Treating Moderador as unable to review Recursos

**Miembro**:
A logged-in user with a verified email who may submit Propuestas and see their own Propuestas with status.
_Avoid_: Anonymous visitor, unverified account

**Cola de revisión**:
The on-site list where Revisores see pending Propuestas and choose Publicación or Rechazo, mirroring the Events pending flow.
_Avoid_: Django admin changelist (as the primary product surface), dashboard app (the Events UI lives under /eventos/, not dashboard/)

**Motivo de rechazo**:
Optional text a Revisor may attach to a Rechazo; visible to the Miembro on their Propuestas and in the in-app notification when present.
_Avoid_: Mandatory rejection essay, silent reject without status

**Enlace canónico**:
The URL that identifies a Recurso for duplicate detection. A new Propuesta is blocked if the same URL already exists on an approved or pending Recurso of the hub.
_Avoid_: Ignoring pending rows when checking duplicates
