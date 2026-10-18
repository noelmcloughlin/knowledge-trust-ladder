<!-- An ingest. The lines above this template are the run's: which entries it looked at, what moved, and what it could not fetch. The workflow writes them; this part is the reviewer's. -->

## What this pull request brings in

Copies of pages and documents that live outside this repository, fetched by the ingest from the places `.lokf/ingest.yaml` names. They sit under `.lokf/mirror/`, one file per page or document, each with a header that says where it came from, which version it was and when it was fetched. They are not knowledge yet. The librarian reads them on its next run and proposes concepts that cite them, and a person confirms those.

## What to check

- [ ] Read the diff as you would read the page: is this text something this repository should hold? A page that should not be here comes out of the manifest, not out of this diff.
- [ ] A line above that says *gone* or *unlisted* names a file whose source went away or left the selection. The file stays until the librarian has asked about the concepts that cite it; the run's `--prune` flag removes one that no concept cites.
- [ ] A line that says *failed* or *refused* names a source the run could not fetch, and why. A missing or expired token is the usual reason; the sidecar's automation page says where tokens go.
- [ ] Merge, and the librarian's next run reads what changed.
