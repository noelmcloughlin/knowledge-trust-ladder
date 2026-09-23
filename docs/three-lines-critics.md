# Critics of the Three Lines Model

> [!NOTE]
> Preliminary research. Each source is quoted from its own text. The list is a starting point, not a literature review.

The model's own critics say its origins are opaque and its effectiveness untested. The UK Parliamentary Commission on Banking Standards (the Commission, below), academics, and the people applying the model to banks and to AI have each questioned its record. Two bodies of research question the kind of tool a bundle is: a machine's output checked by a person. This page takes their points one at a time. Each section says what the criticism is and who made it, what a bundle does about it, and gives one of three verdicts:

- **Met by construction.** The bundle's design removes the ground for the point.
- **Answered in part.** The bundle does something about it, and the section says what is left open.
- **Not the bundle's role.** The point stands, and it lands on the organisation that adopts a bundle.

The [three lines page](three-lines.md) places the roles, says what an auditor can check, and collects every gap left open here by owner.

| The criticism | Raised by | A bundle's answer | Verdict |
| --- | --- | --- | --- |
| [Accountability is diluted across the lines](#accountability-is-diluted-across-the-lines) | the Commission; Davies and Zhivitskaya | one named person per confirmation | Met by construction |
| [The second line cannot challenge the first](#the-second-line-cannot-challenge-the-first) | the Commission; Arndorfer and Minto | the second line is a program | Met by construction |
| [The second line sees only what it is shown](#the-second-line-sees-only-what-it-is-shown) | Zhivitskaya, as Schuett repeats it | the gate reads the whole change and asks the forge | Met by construction, one limit |
| [Process is followed, judgement is absent](#process-is-followed-judgement-is-absent) | the Commission; research on human oversight | source before claim; only a person's verdict is recorded | Answered in part |
| [The machine invents](#the-machine-invents) | Ji et al. | a named source on every record | Answered in part |
| [The lines do not coordinate in practice](#the-lines-do-not-coordinate-in-practice) | Bantleon et al.; Valkenburg and Bongiovanni | every hand-off is written down | Answered in part |
| [Incentives are misaligned, skill is lacking](#incentives-are-misaligned-skill-is-lacking) | Arndorfer and Minto | nothing; the curation policy names curators | Not the bundle's role |
| [Internal audit is weak, so add a fourth line](#internal-audit-is-weak-so-add-a-fourth-line) | Arndorfer and Minto | evidence for a third line, not the review | Not the bundle's role |
| [The model's effectiveness is untested](#the-models-effectiveness-is-untested) | Davies and Zhivitskaya; Schuett | no claim about itself; a sample for whoever tests it | Not the bundle's role |

## Accountability is diluted across the lines

**The criticism.** The Commission found that the three lines "promoted a wholly misplaced sense of security": responsibilities blurred and accountability diluted ([Changing banking for good](https://www.parliament.uk/documents/banking-commission/Banking-final-report-volume-i.pdf), Volume I, conclusions 20 and 134). Davies and Zhivitskaya note that some argue spreading responsibility across lines reduces accountability ([Global Policy, 2018](https://doi.org/10.1111/1758-5899.12568)).

**What a bundle does.** Every confirmation names one person in `verified[].by`. The librarian's own re-checks are `process:`, never a person. Accountability is per claim, not per department.

**Verdict: met by construction.**

## The second line cannot challenge the first

**The criticism.** The Commission's second line "lacked the status to challenge front-line staff effectively", and its remedy was for "these lines to be separate, with distinct authority given to internal control". Arndorfer and Minto count a second line without organisational independence among four weaknesses seen in bank failures ([Financial Stability Institute Occasional Paper 11, 2015](https://www.bis.org/fsi/fsipapers11.pdf)).

**What a bundle does.** The second line is a program. `lokf validate` and the `provenance` job return the same verdict whoever opened the change, written on the pull request where anyone can read it. Whether a failed check blocks a merge is a setting of the host repository, and an organisation that needs the block sets it.

**Verdict: met by construction.** Arndorfer and Minto's other second-line weakness, a lack of skill to challenge, is under [Incentives are misaligned, skill is lacking](#incentives-are-misaligned-skill-is-lacking).

## The second line sees only what it is shown

**The criticism.** Schuett repeats Zhivitskaya's point that a second line "might not recognize that they only see what the first line chooses to show them" ([AI & Society, 2023](https://doi.org/10.1007/s00146-023-01811-0)).

**What a bundle does.** The gate reads the whole pull request and the repository's history, and asks the forge, not the author, whether the named person approved or signed. The Institute of Internal Auditors' 2026 text makes such unfiltered access the condition of independence.

**Verdict: met by construction, with one limit.** The gate sees what the first line wrote, not what it never derived. A missing concept surfaces only as a docent miss.

## Process is followed, judgement is absent

**The criticism.** The Commission saw "a box-ticking exercise whereby processes were followed, but judgement was absent". The research on human oversight of automated systems says why that happens once a machine is in the process:

- People accept a machine's output even when it is wrong, and this "cannot be prevented by training or instructions" ([Parasuraman and Manzey, Human Factors, 2010](https://doi.org/10.1177/0018720810376055)).
- An explanation makes acceptance more likely "regardless of its correctness" ([Bansal et al., CHI 2021](https://doi.org/10.1145/3411764.3445717)).
- Policies that require a human to oversee an algorithm rest on people who "are unable to perform the desired oversight functions" ([Green, Computer Law & Security Review, 2022](https://doi.org/10.1016/j.clsr.2022.105681)).
- People relied less blindly on a machine's suggestion when the screen forced a pause before showing it, and not when it merely added an explanation: asking for their own answer first, showing the suggestion only when they clicked for it, or making them wait for it ([Buçinca et al., CSCW 2021](https://doi.org/10.1145/3449287)).

**What a bundle does.** Four things:

- The curator records only what the person says and confirms nothing itself.
- The review session shows the source before the claim, the pause Buçinca describes.
- Who confirms what, and how often, is a reviewed policy rather than a habit, the direction Green points.
- The docent's evidence-first mode quotes the source before any answer that rests on an unconfirmed concept. It is off by default, because Buçinca found such designs cost goodwill.

Once `revision` ships (proposed for lokf 0.9.0, and for OKF in [knowledge-catalog#437](https://github.com/GoogleCloudPlatform/knowledge-catalog/issues/437)), a confirmation will also say which state of the source it rested on.

**Verdict: answered in part.** Left open:

- Nothing shows that the person read the source. A signature proves who decided, and `revision` names what the skill fetched.
- A page assembled afresh on every request reads as changed on every re-check, which is why the skill prefers a server's ETag to a digest.
- The evidence Green asks for, that oversight works, is third-line work a bundle should not produce about itself. The curator's report hands over a random sample of confirmed concepts when the policy names a size.

## The machine invents

**The criticism.** Text generation produces content "unfaithful to the provided source content" ([Ji et al., ACM Computing Surveys, 2023](https://doi.org/10.1145/3571730)).

**What a bundle does.** Every record names the source it was derived from, so faithfulness can be checked against something. What the librarian cannot settle is marked `status: draft` with an open question until a person decides. The registrar checks what needs no judgement: a local `resource` that no longer exists, and a `revision` naming no commit that holds it. URLs are not fetched.

**Verdict: answered in part.** Left open, by design: the registrar never judges truth, and the librarian's scheduled re-check is the same kind of tool that wrote the text, so it is self-review. The independent judgement is the curator's.

## The lines do not coordinate in practice

**The criticism.** A survey of 415 chief audit executives found coordination between internal audit and the other lines uneven in practice ([Bantleon et al., International Journal of Auditing, 2021](https://doi.org/10.1111/ijau.12201)). A systematic review found the model's use in cybersecurity "fragmented at best" ([Valkenburg and Bongiovanni, Computers & Security, 2024](https://doi.org/10.1016/j.cose.2024.103708)).

**What a bundle does.** It makes no claim about coordination. Its lines hand off through a pull request, the log and the docent's feedback to the librarian, all of which [an auditor can check](three-lines.md#what-an-auditor-can-check).

**Verdict: answered in part.** The hand-offs are written down. Whether the lines coordinate beyond them is not something a bundle shows.

## Incentives are misaligned, skill is lacking

**The criticism.** Arndorfer and Minto's remaining two weaknesses: misaligned incentives in the first line, and a second line without the skill to challenge the first.

**What a bundle does.** Nothing. LOKF does not ask its second line to judge content, so that judgement lands on the curator, a named person in the first line. The organisation assigns curators through the curation policy and answers for their incentives and skill.

**Verdict: not the bundle's role.**

## Internal audit is weak, so add a fourth line

**The criticism.** Arndorfer and Minto's fourth weakness is an internal audit whose risk assessment is inadequate or subjective. Their remedy is a fourth line: external audit and supervisors.

**What a bundle does.** It ships the evidence a third line needs, and not the review, since assurance is independent only when it comes from someone other than the authors. A fourth line is the organisation's to add.

**Verdict: not the bundle's role.** An auditor skill for the third line is listed under [What remains to do](three-lines.md#what-remains-to-do-and-who-does-it).

## The model's effectiveness is untested

**The criticism.** Davies and Zhivitskaya find the model's origins opaque and its effectiveness untested. Schuett notes that "the model has been criticized and there is not much empirical evidence for its effectiveness", and concludes that within its limits it "can plausibly contribute to a reduction of risks from AI".

**What a bundle does.** It claims nothing about the model. LOKF was not built to it; the [three lines page](three-lines.md) uses the model to answer three questions: who is accountable for a claim, what a machine checks, and what can be examined afterwards. Whether the arrangement reduces risk is for a third line to test, and the curator's report hands over a random sample of confirmed concepts when the policy names a size.

**Verdict: not the bundle's role.**

Every gap left open above is collected, by owner, under [What remains to do, and who does it](three-lines.md#what-remains-to-do-and-who-does-it).

## Sources

- Parliamentary Commission on Banking Standards (2013). *Changing banking for good*, Volume I. <https://www.parliament.uk/documents/banking-commission/Banking-final-report-volume-i.pdf>
- Davies, H. and Zhivitskaya, M. (2018). Three Lines of Defence: A Robust Organising Framework, or Just Lines in the Sand? *Global Policy* 9(S1), 34–42. <https://doi.org/10.1111/1758-5899.12568>
- Arndorfer, I. and Minto, A. (2015). The "four lines of defence model" for financial institutions. *Financial Stability Institute Occasional Paper* 11. <https://www.bis.org/fsi/fsipapers11.pdf>
- Schuett, J. (2023). Three lines of defense against risks from AI. *AI & Society*. <https://doi.org/10.1007/s00146-023-01811-0>
- Bantleon, U., d'Arcy, A., Eulerich, M., Hucke, A., Pedell, B. and Ratzinger-Sakel, N. V. S. (2021). Coordination challenges in implementing the three lines of defense model. *International Journal of Auditing* 25(1), 59–74. <https://doi.org/10.1111/ijau.12201>
- Valkenburg, B. and Bongiovanni, I. (2024). Unravelling the three lines model in cybersecurity: a systematic literature review. *Computers & Security* 139, 103708. <https://doi.org/10.1016/j.cose.2024.103708>
- Parasuraman, R. and Manzey, D. H. (2010). Complacency and Bias in Human Use of Automation: An Attentional Integration. *Human Factors* 52(3), 381–410. <https://doi.org/10.1177/0018720810376055>
- Bansal, G., Wu, T., Zhou, J., Fok, R., Nushi, B., Kamar, E., Ribeiro, M. T. and Weld, D. (2021). Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance. *CHI 2021*. <https://doi.org/10.1145/3411764.3445717>
- Green, B. (2022). The flaws of policies requiring human oversight of government algorithms. *Computer Law & Security Review* 45, 105681. <https://doi.org/10.1016/j.clsr.2022.105681>
- Buçinca, Z., Malaya, M. B. and Gajos, K. Z. (2021). To Trust or to Think. *Proceedings of the ACM on Human-Computer Interaction* 5(CSCW1), 1–21. <https://doi.org/10.1145/3449287>
- Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y. J., Madotto, A. and Fung, P. (2023). Survey of Hallucination in Natural Language Generation. *ACM Computing Surveys* 55(12), 1–38. <https://doi.org/10.1145/3571730>
