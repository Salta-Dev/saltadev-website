# Propuestas de Recursos se revisan en la web como Eventos

Community Recursos submissions (Lectura, Herramientas, Proyectos, Cursos) are reviewed on the site by Revisores (Administrador or Moderador), with a pending queue and Publicación/Rechazo — the same pattern as Events under `/eventos/`, not Django admin as the primary surface.

**Considered options**: Django-admin-only approval (fast, already partially built for catalog); a separate “dashboard app” screen. Rejected admin-only because Revisores already moderate Events in-product and Moderadores would be excluded from the current catalog admin gate.

**Consequences**: Cursos keep their own model but gain the same Propuesta lifecycle; Miembros get “Mis propuestas”; in-app notifications fire on Publicación/Rechazo.
