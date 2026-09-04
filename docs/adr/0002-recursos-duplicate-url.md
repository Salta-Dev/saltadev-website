# Duplicate Recursos blocked by canonical URL

A Propuesta is rejected at submit time when another hub Recurso (approved or still pending) already uses the same canonical URL. This prevents double listings from retries and copy-paste submissions.

**Considered options**: warn-only; allow duplicates; check approved-only. Rejected those because pending rows would still collide at Publicación time and create noisy queues.
