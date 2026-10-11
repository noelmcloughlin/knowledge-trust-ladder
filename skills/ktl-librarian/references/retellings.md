# Retellings: concepts for younger readers

This page is for **ktl-librarian** when it writes or refreshes a retelling: a concept that tells younger readers what another concept says, in shorter words. It gives the one rule that changes, where a retelling lives, when a run may write one, and what to check after.

## The rule that gives way

Section 1 of the skill page says to carry each fact as its source states it: add no qualifier the source lacks, and drop none it has. For a retelling, the source is the adult concept it retells, and the rule gives way in one direction only. Say nothing the adult concept does not say. A retelling may leave a fact out, and it never adds one, rounds a number or brings in an analogy.

ktl-prose's [young-readers.md](../../ktl-prose/references/young-readers.md) gives the two bands of age, their limits, the rules a retelling adds, and where an explanation or an example may come from. Read it before you write the first retelling of a session.

## Writing one

Create the retelling through the pen, as a new concept:

- **Its path** is `young-readers/` and the adult concept's file name, in one flat folder at the top of the bundle.
- **Its frontmatter** has the adult concept's `type`, `genre`, `about` and `resource`, and every other field the class requires. Its `title` names the band, and its `description` says who it is for and what it retells. `derivedFrom` names the adult concept's `id`. A `sources` entry gives the adult concept's own path from the repository root, such as `.lokf/knowledge/glossary/the-pen.md`. `tags` carries the band, such as `audience-13-18`.
- **Its body** opens by saying who it is for, and links the adult concept: "This page is for readers aged 13 to 18. It retells [[the-pen]] in shorter words. The full page has every detail."

```yaml
ops:
  - op: create
    path: young-readers/the-pen.md
    frontmatter:
      type: GlossaryTerm
      title: The pen, for readers aged 13 to 18
      description: The pen retold for readers aged 13 to 18, the script through which ktl-librarian writes every change to the bundle.
      definition: The script through which ktl-librarian writes every change to the bundle.
      genre: reference
      resource: skills/ktl-sidecar/templates/scripts/knowledge-apply.sh
      derivedFrom:
        - https://knowledge-trust-ladder.example/knowledge/glossary/the-pen
      sources:
        - resource: .lokf/knowledge/glossary/the-pen.md
      tags:
        - audience-13-18
    body: |
      This page is for readers aged 13 to 18. It retells [[the-pen]] in shorter words. The full page has every detail.
    log: "**Added**: The pen, retold for readers aged 13 to 18 from `glossary/the-pen.md`."
```

The `sources` entry puts the retelling on the work list whenever the adult concept's file changes.

## Refreshing one

A concept whose `derivedFrom` names another concept of the bundle, and whose `tags` carry a band, is a retelling. Re-derive it from that concept as it now stands, never from the repository. Leave out what the adult concept no longer says, and carry over nothing it never said.

## When a run may write one

- **In a live session**, when a person asks for one.
- **On a scheduled run**, only for a band that the curation policy's `Younger readers:` line declares, and only from a concept a person has confirmed. A retelling of a draft would retell claims nobody has checked.
- **Never** because a reader's feedback entry asks for one. Name the request in the hand-off, and let a person decide.

## After writing one

Where ktl-prose is installed, check the retelling with its script, from the repository root:

```sh
python3 <ktl-prose>/scripts/prose-check.py .lokf/knowledge/young-readers/the-pen.md
python3 <ktl-prose>/scripts/prose-check.py --derived-from .lokf/knowledge/glossary/the-pen.md .lokf/knowledge/young-readers/the-pen.md
```

The first holds the retelling to its band's limits, and the second shows it adds nothing the adult concept does not hold. Fix each finding with a `rewrite`. In the hand-off, name each retelling, what it left out, and the adult concept a curator confirms it against.
