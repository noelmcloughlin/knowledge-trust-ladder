<!-- An ingest. The lines above are the run's report: what it fetched, what changed and what it could not fetch. -->

## What this brings in

Copies of pages and documents from outside this repository, fetched from the places `.lokf/ingest.yaml` names into `.lokf/mirror/`. They are not knowledge yet: the librarian reads them on its next run after the merge.

## Reviewer checklist

- [ ] The diff holds text this repository should keep. To drop a page, remove it from `.lokf/ingest.yaml`, not from this diff.
- [ ] Any source marked *failed* above is followed up. An expired token is the usual cause.
