# For the curious: how a claim gets checked, and where the vocabulary ends

[The README](../README.md) says everything you need to decide whether to install these skills. What follows is the mechanics: exactly what "confirmed by a person" is standing on, and what to do when a bundle outgrows the built-in vocabulary.

## Four levels of checking

Each proves less than its name suggests. Only the third yields a claim someone has agreed to stand behind.

| Check | Who, when | What it proves | What it can't |
| --- | --- | --- | --- |
| Schema-valid | the `lokf` toolkit on every change (`just lokf-validate`, and `just lokf-check-refs` for relation targets); `lokf validate` again as the CI gate on every pull request that touches the bundle | the frontmatter is well-formed, the types and relations are ones the schema knows, and every typed relation points at a concept that exists | that anything in it is true |
| Source-consistent | `lokf-librarian` on every scheduled refresh - shown as *checked by automation only* | the concept still matches what its source says today | that the source is right, or that the concept says what the team means |
| Human-confirmed | a named person, through `lokf-curator` or the LOKF Curator plugin - shown as *confirmed by a person* | someone accountable read the source and agreed | that it stays true - which is what review dates are for |
| Proven in use | readers, through `lokf-docent`, which records misses and disagreements in `.lokf/feedback.md` | the bundle answered a real question - or didn't, and the gap became the librarian's next task | nothing further - this is the feedback loop that feeds the other three |

The first and third rows also run live, outside these skills and the CLI, for anyone maintaining a bundle in Obsidian rather than through an agent: LOKF Registrar for the first, LOKF Curator for the third - see [the fifth role](../README.md#the-fifth-role-which-is-not-a-skill).

## When the vocabulary stops fitting

LOKF's vocabulary is deliberately small - 15 classes, ten typed relations - which is what keeps bundles portable. When concepts stop fitting those classes, typically in a deep or safety-critical domain (medicine, law, finance, safety engineering), the answer is a domain schema written in [LinkML](https://linkml.io) that extends LOKF's, not a looser bundle. The curator flags the drift; the team decides; the librarian applies it. What it costs (no new tooling), how to write one, what to do when the domain already has a LinkML vocabulary of its own, and how to validate values it binds to an external domain ontology: [`lokf-curator/references/domain-schemas.md`](../skills/lokf-curator/references/domain-schemas.md).
