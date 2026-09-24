# The docent in Microsoft 365 Copilot

This folder builds **ktl-docent-m365**, a custom skill for a Microsoft 365 Copilot declarative agent. It is an integration point, not a fifth skill. It carries the docent's discipline into Copilot, and the other three skills stay in the repository, where they have git, a shell and a forge.

Copilot runs a skill in a sandbox with no repository, no shell and no network. So the build packs a **snapshot** of one bundle into the skill, and the docent answers from that snapshot. It says how far each concept has been trusted, as ktl-docent does, and it names the snapshot's revision and build date in every answer. It cannot check a value at its source or write `.lokf/feedback.md`. It says the first, and hands each gap back to the reader as a line to file.

## Build it

Run the build from a clone of this repository. Point it at a bundle directory, or at a release's `knowledge-<tag>-<repository>.zip`:

```bash
integrations/m365/build.sh ../my-repo/.lokf/knowledge ./dist
integrations/m365/build.sh --repo-url https://github.com/me/my-repo knowledge-v1.2.0-my-repo.zip ./dist
```

It creates `./dist/ktl-docent-m365/`:

```text
ktl-docent-m365/
  SKILL.md      the Copilot instructions, copied from skill-template.md
  SNAPSHOT.md   the repository, revision and build date, a source link pattern, and where to report gaps
  knowledge/    the bundle, copied unchanged
```

A directory in a git work tree gives the repository URL and the revision by itself. A zip gives the tag from its name, and `--repo-url` adds the repository; without it, answers give a concept's source as a bare path.

The build checks the result against Copilot's limits for custom skills and writes nothing when one fails. It exits 1 in that case and names each problem:

| Limit | Why it can fail |
| --- | --- |
| SKILL.md under 20,000 characters | never, unless the template grows |
| directory depth of 3 | a bundle with folders nested three deep under `knowledge/` |
| allowed file types | anything in the bundle other than Markdown and the other listed types |
| 350 files across all of an agent's skills | a bundle of more than about 340 concepts |
| 10 MB for the whole app package | a very large bundle |

The build also refuses a bundle that holds symbolic links, so nothing outside the bundle reaches the package.

## Add it to an agent

1. Install the [Microsoft 365 Agents Toolkit CLI](https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/microsoft-365-agents-toolkit-cli) with `npm install -g @microsoft/m365agentstoolkit-cli`.
2. Create a declarative agent with `atk new -c declarative-agent -n my-docent -i false`, or open one you have.
3. Zip the built directory and add it. `atk add skill` is a preview command, hidden until `ATK_FRONTIER=true` is set, and its `--from` takes a zip from any path; a directory it takes only from inside `appPackage/`.

   ```bash
   (cd ./dist && zip -r ../ktl-docent-m365.zip ktl-docent-m365)
   ATK_FRONTIER=true atk add skill --from ./ktl-docent-m365.zip -i false
   ```

   The command checks the frontmatter and the name only. The limits in the table above are the service's, which is why the build checks them first.
4. Run `atk validate`, then `atk provision`, and try it with `atk preview`.

Custom skills are a preview feature, so these limits apply:

- Your tenant must be in the Microsoft Frontier preview program.
- An agent cannot have both custom skills and embedded knowledge files yet.
- Tenants that use Purview Information Barriers have no custom skills at all.
- Partner Center does not accept agents with custom skills yet.

## Keep it current

The snapshot does not update itself. Rebuild the skill and provision again after each release that changes the bundle. The release's zip is the natural input, because it is the bundle exactly as that release shipped it. Gap reports that readers file go to the repository, where the librarian turns them into concepts on its next run and a person confirms them with the curator.

## Why only the docent

The other three skills need a repository, a shell and a forge, and Copilot's sandbox has none of them. The curator could follow one day, in two parts. Its identity would change from a forge login to a Microsoft Entra actor (tenant, object id, and how sure the host is of it), which is a host's [domain schema](../skills/ktl-curator/references/domain-schemas.md) to declare, not this repository's: a subclass of the verification event carrying those fields, validated with `lokf validate --schema`. Its writes would need an action the agent can call, because a declarative agent's SharePoint capability reads and searches only. Neither part exists yet.

## Change the instructions

Edit [skill-template.md](skill-template.md). It is named that way, not `SKILL.md`, so that skill installers and catalogs do not list it as a fifth skill. Its trust-label table must match ktl-docent's word for word, and the repository contract checks that.
