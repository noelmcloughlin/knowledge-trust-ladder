# ktl-website, the bundle's website

This page is for anyone who wants a bundle that people can browse.

`ktl-website` builds a website for the bundle, and it is optional. The site has a page for each concept with its trust label, a health page, a knowledge graph, and search by trust and type.

| | |
| --- | --- |
| **Played by** | the [`ktl-website`](../../skills/ktl-website/SKILL.md) skill, an agent |
| **Runs** | once, after the [sidecar](sidecar.md), and again to repair or update the site |
| **Writes** | `website/`, an Astro Starlight site, and a workflow that publishes it to GitHub Pages |
| **Never** | writes into the bundle, the README or the docs |

## Ask it

- "Publish the knowledge bundle as a website."
- "Update the website this skill installed."

## Where the rest is written

- **What it needs installed**: [install.md](../install.md#what-each-skill-needs).
- **Every option the site takes**: the skill's [customising page](../../skills/ktl-website/references/customising.md).
- **Another forge than GitHub**: the skill's [deploy page](../../skills/ktl-website/references/deploy.md#another-forge).
- **Sites built this way**: [this repository's own](https://w3id.org/ktl/).
