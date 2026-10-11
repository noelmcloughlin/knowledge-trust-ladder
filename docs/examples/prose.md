# Examples: `ktl-prose` writing for younger readers

Captured runs of `ktl-prose` on this repository, following `skills/ktl-prose/references/young-readers.md`. The commands ran from the repository root, and the output is real, cut only where a line says so.

## 1. A README for readers aged 13 to 18

The request was a version of `README.md` for readers aged 13 to 18. Outside the bundle, ktl-prose writes a retelling itself, in a new file beside the original, as `references/other-files.md` describes under *A version for younger readers*.

**The original, at the band's limits.** The README passes the adult limits. At the limits for 13 to 18 it has 31 sentences over 20 words and one paragraph over 75 words:

```text
$ python3 skills/ktl-prose/scripts/prose-check.py --audience 13-18 README.md
note: README.md:1: grade: Automated Readability Index 7.9, from 16.1 words a sentence and 4.5 letters or digits a word, with 21% of the words seven letters or longer; the 13-18 target is 9 or under
note: README.md:1: vocabulary: 232 of 1123 words are outside the VOA Learning English word book, most often: checks (12), bundle (11), agent (8), schema (6), plugin (5), librarian (5), concepts (5), confirmation (4), registrar (4), toolkit (4); explain each where it first appears, or choose a plainer word
README.md:13: long: 23 words in one sentence, and the limit is 20: "Knowledge Trust Ladder keeps a repository's scattered knowledge..."
README.md:13: long: 23 words in one sentence, and the limit is 20: "Registrar automation checks every record and guards every..."
(30 more findings cut)
```

**The retelling, at its own band.** `README.en-simple.md` opens with "This page is for readers aged 13 to 18.", so a plain style run holds it to that band:

```text
$ python3 skills/ktl-prose/scripts/prose-check.py README.en-simple.md
note: README.en-simple.md:3: audience: the page says it is for readers aged 13 to 18, so the 13-18 limits apply
note: README.en-simple.md:1: grade: Automated Readability Index 4.3, from 10.4 words a sentence and 4.4 letters or digits a word, with 18% of the words seven letters or longer; the 13-18 target is 9 or under
note: README.en-simple.md:1: vocabulary: 119 of 664 words are outside the VOA Learning English word book, most often: bundle (12), checked (9), entry (7), source (5), agent (4), concept (4), roles (4), label (4), repository (3), librarian (3); explain each where it first appears, or choose a plainer word
OK: 1 file(s), and nothing a script can see breaks the style rules or hides from a reader
```

**What it adds to the original: nothing.** Every link, number, code span and quotation in the retelling is in the README. What the retelling left out is a note:

```text
$ python3 skills/ktl-prose/scripts/prose-check.py --derived-from README.md README.en-simple.md
note: README.en-simple.md:1: link: 40 link targets of the adult text left out
note: README.en-simple.md:1: digits: 3 numbers of the adult text left out: "1922", "2026", "365"
note: README.en-simple.md:1: code: 11 code spans of the adult text left out: ".lokf/knowledge/", ".lokf/knowledge/index.md", "gh skill", "human:", "knowledge_bundle", and more
note: README.en-simple.md:1: quote: 8 quotations of the adult text left out: (cut)
note: README.en-simple.md:1: fence: 1 fenced block of the adult text left out
OK: the retelling holds nothing the adult text does not (1 file): 802 words, and the adult text has 1895
```

**The hand-off.**

- **Band** 13 to 18. The README holds 1,895 words of prose, and the retelling 802.
- **Left out:** the epigraph, the paragraphs on OKF and WikiSkill, the three lines of defence, the Obsidian plugins in detail, the Claude Code plugin and Microsoft 365 installs, most of the reading table, and most of the credits.
- **Explanations, each from the README itself:** a deterministic check "gives the same answer every time"; a docent is "a museum's name for a guide"; `.lokf/` is a folder beside the code like `.git/`; and the bundle sits between the sources and whoever reads them, as the README's context layer does. CI is written out as continuous integration.
- **Left unexplained,** because the README defines none of them: repository, agent, Markdown and pull request. Source, agent and concept are among the words the vocabulary note names.
- **Who checks:** the person who reads the pull request, against `README.md`. No script shows the retelling is easier to read. Reading it with readers aged 13 to 18 is the test.

## 2. The first retelling in the bundle

The request was a retelling of `glossary/the-pen.md` for readers aged 13 to 18, in this repository's own bundle. In the bundle, ktl-librarian writes a retelling through the pen, as its `references/retellings.md` says, and ktl-prose checks it.

**Through the pen.** One `create` operation in `.lokf/patch.yaml`, in the shape `references/retellings.md` shows:

```text
$ bash .lokf/scripts/knowledge-apply.sh
wrote .lokf/knowledge/young-readers/the-pen.md
wrote .lokf/knowledge/young-readers/index.md
wrote .lokf/knowledge/index.md
wrote .lokf/knowledge/log.md
OK - 1 operation(s) by process:ktl-librarian at 2026-10-11T15:00:59Z; now run lokf validate --check-refs and knowledge-conventions.sh
```

**At its band, and against the adult concept.** The two links the adult concept does not hold go to glossary concepts, and explain a term each:

```text
$ python3 skills/ktl-prose/scripts/prose-check.py .lokf/knowledge/young-readers/the-pen.md
note: .lokf/knowledge/young-readers/the-pen.md:23: audience: the page says it is for readers aged 13 to 18, so the 13-18 limits apply
note: .lokf/knowledge/young-readers/the-pen.md:1: grade: Automated Readability Index 2.0, from 9.4 words a sentence and 4.0 letters or digits a word, with 15% of the words seven letters or longer; the 13-18 target is 9 or under
note: .lokf/knowledge/young-readers/the-pen.md:1: vocabulary: 29 of 177 words are outside the VOA Learning English word book, most often: file (4), pen (4), page (2), bundle (2), readers (1), docs (1), script (1), edits (1), hand (1), checks (1); explain each where it first appears, or choose a plainer word
OK: 1 file(s), and nothing a script can see breaks the style rules or hides from a reader

$ python3 skills/ktl-prose/scripts/prose-check.py --derived-from .lokf/knowledge/glossary/the-pen.md .lokf/knowledge/young-readers/the-pen.md
note: .lokf/knowledge/young-readers/the-pen.md:27: link: "knowledge-bundle" is a concept the adult text does not link; keep it only where it explains a term
note: .lokf/knowledge/young-readers/the-pen.md:51: link: "registrar" is a concept the adult text does not link; keep it only where it explains a term
note: .lokf/knowledge/young-readers/the-pen.md:1: code: 2 code spans of the adult text left out: ".lokf/questions.md", "handoff"
OK: the retelling holds nothing the adult text does not (1 file): 238 words, and the adult text has 271
```

`lokf validate --check-refs` then passed on all 42 concepts, and so did the conventions script.

**The index section.** The pen named the new section after the folder, `# Young-readers`. A person renamed it "Young readers", once, and added a line that links the folder's own `index.md`. The pen finds a section by that link, so a second retelling, made in a scratch copy of the bundle, went under the same heading.

**What the retrieval score did.** The score reads the index alone. This repository's ledger held no reader's question in words yet, so the check used 12 questions about adult concepts and 2 asked for younger readers, written for the test. An agent answered each prompt from the index alone, twice before the retelling and twice after:

| Run | Adult questions that reached their concept | Questions for younger readers |
| --- | --- | --- |
| Before, first | 12 of 12 | left out, with no concept to reach |
| Before, second | 12 of 12 | left out, with no concept to reach |
| After, first | 12 of 12 | 2 of 2 |
| After, second | 12 of 12 | 2 of 2 |

After the retelling, it appeared in one adult answer per run, for "Which script refuses a patch that adds a human: actor?", second after the adult concept. For both questions for younger readers it came first. So the section for younger readers did not move the score for adult questions here. The test is small: 42 concepts, one retelling, questions written for it, and one small model, Claude Haiku.

**Still to do: the confirmation.** A curator confirms a retelling against the adult concept, and only a person can. Until a person does so with ktl-curator, the retelling is a draft that nobody has checked yet.
