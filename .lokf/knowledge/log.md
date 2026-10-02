# Change Log

## 2026-10-02

* **Refresh**: the ktl-librarian skill concept follows its source again. The skill now reads the curator's verdicts before it derives, handles at most ten feedback entries in a run, treats a miss on a covered question as a description defect, and states what a `description` must do.
* **Prose**: reworded 12 concept bodies in plain English, splitting 16 sentences that ran past 40 words into shorter ones or lists. No fact, link, number or frontmatter changed; `prose-check.py --against HEAD` reports wording only.
* **Rebuild**: derived 34 concepts again from the repository's README, docs and skill pages, after a plain-prose pass over those sources. The earlier bundle was emptied first, so that no confirmation rests on a source whose text changed under it. Every concept starts as a draft, and the ktl-prose playbook is new.
* **Removal**: the two placeholder services the sidecar laid down are gone; this repository has no services.
* **Initialization**: Scaffolded the LOKF bundle for Knowledge Trust Ladder with placeholder
  services. Real concepts to follow.
