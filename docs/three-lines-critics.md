# Critics of the Three Lines Model

> [!NOTE]
> Preliminary research. These sources were read and are quoted from their own text. The list is a starting point, not a literature review.

The model's own critics say its origins are opaque and its effectiveness untested. A parliamentary commission, academics, and the people applying it to banks and to AI have each questioned its record. Five readings of the model are quoted here from their own texts, and after them two bodies of research that question the kind of tool a bundle is: a machine's output checked by a person. The [second half of this page](#what-a-bundle-answers-and-what-it-leaves-open) sets against them what a bundle answers, what it leaves open, and what kind of gap each remainder is. The [three lines page](three-lines.md) places the roles, says what an auditor can check, and ends with whose each remaining gap is.

## The UK Parliamentary Commission on Banking Standards (2013)

The three lines "promoted a wholly misplaced sense of security": responsibilities blurred, accountability diluted, a second line that "lacked the status to challenge front-line staff effectively", and "a box-ticking exercise whereby processes were followed, but judgement was absent". Its remedy: "these lines to be separate, with distinct authority given to internal control" ([Changing banking for good](https://www.parliament.uk/documents/banking-commission/Banking-final-report-volume-i.pdf), Volume I, conclusions 20 and 134).

A bundle's answer: accountability per claim, and a second line that is a program, are both [met by construction](#what-a-bundle-answers-and-what-it-leaves-open). The box-ticking point is [answered only in part](#judgement-absent-while-process-is-followed).

## Davies and Zhivitskaya (2018)

[Three Lines of Defence: A Robust Organising Framework, or Just Lines in the Sand?](https://doi.org/10.1111/1758-5899.12568), Global Policy. The model's origins are opaque and its effectiveness untested; some argue that spreading responsibility across lines reduces accountability.

A bundle's answer: accountability is per claim, [met by construction](#what-a-bundle-answers-and-what-it-leaves-open).

## Arndorfer and Minto (2015)

[The "four lines of defence model" for financial institutions](https://www.bis.org/fsi/fsipapers11.pdf), Financial Stability Institute Occasional Paper 11. Four weaknesses seen in bank failures: misaligned incentives in the first line, a second line without organisational independence, a second line without the skill to challenge the first, and an internal audit whose risk assessment is inadequate or subjective. They add a fourth line: external audit and supervisors.

A bundle's answer: the second line's independence is [met by construction](#what-a-bundle-answers-and-what-it-leaves-open). Incentives and skill are [not the bundle's role](#incentives-and-skill), and a fourth line is the organisation's to add; [what remains](three-lines.md#what-remains-to-do-and-who-does-it) says whose.

## Schuett (2023)

[Three lines of defense against risks from AI](https://doi.org/10.1007/s00146-023-01811-0), AI & Society. Applies the model to organisations that build AI. Notes that "the model has been criticized and there is not much empirical evidence for its effectiveness", repeats Zhivitskaya's critique that the second line "might not recognize that they only see what the first line chooses to show them", and concludes that within its limits the model "can plausibly contribute to a reduction of risks from AI".

A bundle's answer: the gate reads the whole pull request and the repository's history, [met by construction](#what-a-bundle-answers-and-what-it-leaves-open) with one stated limit.

## Bantleon et al. (2021) and Valkenburg and Bongiovanni (2024)

[Coordination challenges in implementing the three lines of defense model](https://doi.org/10.1111/ijau.12201), International Journal of Auditing: a survey of 415 chief audit executives found coordination between internal audit and the other lines uneven in practice. [Unravelling the three lines model in cybersecurity: a systematic literature review](https://doi.org/10.1016/j.cose.2024.103708), Computers & Security: the model's use in cybersecurity has been "fragmented at best".

A bundle's answer: no claim about coordination is made. A bundle's lines hand off through a pull request, the log and the docent's feedback to the librarian, all of which [an auditor can check](three-lines.md#what-an-auditor-can-check).

## Research on human oversight of automated systems

People accept a machine's output even when it is wrong, and this "cannot be prevented by training or instructions" ([Complacency and Bias in Human Use of Automation](https://doi.org/10.1177/0018720810376055), Parasuraman and Manzey, Human Factors, 2010). Explanations make acceptance more likely "regardless of its correctness" ([Does the Whole Exceed its Parts?](https://doi.org/10.1145/3411764.3445717), Bansal et al., CHI 2021). Policies that require a human to oversee an algorithm rest on people who "are unable to perform the desired oversight functions" ([The flaws of policies requiring human oversight of government algorithms](https://doi.org/10.1016/j.clsr.2022.105681), Green, Computer Law & Security Review, 2022). People relied less blindly on a machine's suggestion when the screen forced a pause before showing it, and not when it merely added an explanation: asking for their own answer first, showing the suggestion only when they clicked for it, or making them wait for it ([To Trust or to Think](https://doi.org/10.1145/3449287), Buçinca et al., CSCW 2021).

A bundle's answer: [answered in part](#judgement-absent-while-process-is-followed). The curator records only what the person says and sees the source before the claim, the docent's evidence-first mode is a policy switch, and nothing can show that anyone read.

## Research on text generation

Text generation produces content "unfaithful to the provided source content" ([Survey of Hallucination in Natural Language Generation](https://doi.org/10.1145/3571730), Ji et al., ACM Computing Surveys, 2023).

A bundle's answer: [answered in part](#the-machine-invents). Every record names its source and the registrar fails on a source that has gone, but the judgement of faithfulness is the curator's.

## What a bundle answers, and what it leaves open

Three of the critics' points are met by construction:

- **Accountability diluted** ([the Commission](#the-uk-parliamentary-commission-on-banking-standards-2013); [Davies and Zhivitskaya](#davies-and-zhivitskaya-2018)). Every confirmation names one person in `verified[].by`, and the librarian's own re-checks are `process:`, never a person. Accountability is per claim, not per department.
- **A second line without the status to challenge the first** ([the Commission](#the-uk-parliamentary-commission-on-banking-standards-2013); [Arndorfer and Minto](#arndorfer-and-minto-2015)). The second line is a program: `lokf validate` and the `provenance` job return the same verdict whoever opened the change, written on the pull request where anyone can read it. Whether a failed check blocks a merge is a setting of the host repository, and an organisation that needs the block sets it.
- **A second line that sees only what the first line shows it** ([Zhivitskaya, as Schuett repeats it](#schuett-2023)). The gate reads the whole pull request and the repository's history, and asks the forge, not the author, whether the named person approved or signed; the IIA's 2026 text makes such unfiltered access the condition of independence. It sees what the first line wrote, not what it never derived: a missing concept surfaces only as a docent miss.

Two critiques aim at the kind of solution LOKF is, a machine's output checked by a person, and are answered in part.

### Judgement absent while process is followed

People accept a machine's output even when it is wrong, an explanation makes that more likely, and only a forced pause helps ([the research on human oversight](#research-on-human-oversight-of-automated-systems)). A bundle answers with four things: the curator records only what the person says and confirms nothing itself; the review session shows the source before the claim, the pause Buçinca describes; who confirms what, and how often, is a reviewed policy rather than a habit, the direction Green points; and the docent's evidence-first mode quotes the source before any answer that rests on an unconfirmed concept, off by default because Buçinca found such designs cost goodwill. Once `revision` ships (proposed for lokf 0.9.0 and for OKF in [knowledge-catalog#437](https://github.com/GoogleCloudPlatform/knowledge-catalog/issues/437)), a confirmation will also say which state of the source it rested on.

Left open: nothing shows that the person read the source, since a signature proves who decided and `revision` names what the skill fetched; a page assembled afresh on every request reads as changed on every re-check, which is why the skill prefers a server's ETag to a digest; and the evidence Green asks for, that oversight works, is third-line work a bundle should not produce about itself - the curator's report hands over a random sample of confirmed concepts when the policy names a size.

### The machine invents

Text generation produces content unfaithful to its source ([the research on text generation](#research-on-text-generation)). A bundle answers with two things: every record names the source it was derived from, so faithfulness can be checked against something; and what the librarian cannot settle is marked `status: draft` with an open question until a person decides.

Left open, by design: the registrar never judges truth, and the librarian's scheduled re-check is the same kind of tool that wrote the text, so it is self-review; the independent judgement is the curator's. What the registrar does check needs no judgement: a local `resource` that no longer exists, and a `revision` naming no commit that holds it. URLs are not fetched.

### Incentives and skill

Not the bundle's role. LOKF does not ask its second line to judge content, so that judgement lands on the curator, a named person in the first line; the organisation assigns curators through the curation policy and answers for their incentives and skill.

The gaps left open across the three sections above are collected, by owner, under [What remains to do, and who does it](three-lines.md#what-remains-to-do-and-who-does-it).
