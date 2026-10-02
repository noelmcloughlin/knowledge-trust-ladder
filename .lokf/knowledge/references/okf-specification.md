---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/okf-specification
title: "OKF specification (v0.2)"
description: "Google Cloud's Open Knowledge Format: a folder of Markdown concept files with YAML frontmatter that requires only `type`, plus the v0.2 provenance, trust and lifecycle fields LOKF makes queryable."
genre: reference
resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
sources:
- resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- resource: skills/ktl-librarian/SKILL.md
- resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
  - https://knowledge-trust-ladder.example/knowledge/glossary/okf
---

# Overview

The Open Knowledge Format specification lives in Google Cloud's `knowledge-catalog` repository on GitHub. The README credits Google Cloud as its creator and says LOKF profiles it.

# The parts this family relies on

- Section 5 defines the trust, provenance and lifecycle families: `generated` (who produced the current content, and when), `verified` (a list of verification events), `sources`, `status` and `stale_after`. The librarian records them only where the source attests them, and never invents one.
- Section 5.2 defines `generated.at` as the content's last meaningful change, which is why a rewording by ktl-prose does not move it.
- Section 7 defines actor strings: `human:<id>`, `process:<id>` or `<producer>/<version>`, carried as plain literals and never turned into IRIs.
- Section 9 makes an ISO-date heading in `log.md` a MUST, which the gate's first convention enforces.

The librarian skill notes that OKF permits an unquoted datetime, a bare `verified` mapping, any file name and any YAML. The gate's house rules ask more than that, so that a datetime reaches every consumer as one string and an event reads the same to a line reader as to a parser. Every reader here still accepts a bare mapping, as OKF requires.
