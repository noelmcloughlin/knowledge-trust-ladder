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
