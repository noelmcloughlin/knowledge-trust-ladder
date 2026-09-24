# The docent in Microsoft 365 Copilot

This folder builds **ktl-docent-m365**, a custom skill for a Microsoft 365 Copilot declarative agent. It is not a fifth skill. It puts ktl-docent into Copilot.

Copilot runs skills with no repository, shell or network. So the build copies a **snapshot** of the bundle into the skill, and the docent answers from it. Each answer names the snapshot and how far each concept has been trusted. The docent cannot check a source or write `.lokf/feedback.md`, so it says so and gives the reader a gap report to file.

## Build it

Point the build at a bundle folder or a release zip:

```bash
integrations/m365/build.sh ../my-repo/.lokf/knowledge ./dist
integrations/m365/build.sh --repo-url https://github.com/me/my-repo knowledge-v1.2.0-my-repo.zip ./dist
```

It creates `./dist/ktl-docent-m365/` with `SKILL.md`, `SNAPSHOT.md` (repository, revision, build date) and `knowledge/`. A folder in a git clone gives the repository and revision. A zip gives the tag, and `--repo-url` gives the repository.

The build writes nothing and exits 1 if the result breaks one of Copilot's limits:

- `SKILL.md` over 20,000 characters
- folders more than 3 deep
- file types Copilot does not accept
- more than 350 files
- more than 10 MB
- symbolic links

## Add it to an agent

1. Install the [Agents Toolkit CLI](https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/microsoft-365-agents-toolkit-cli): `npm install -g @microsoft/m365agentstoolkit-cli`.
2. Create an agent, or use one you have: `atk new -c declarative-agent -n my-docent -i false`.
3. Zip the skill and add it. The command is hidden unless `ATK_FRONTIER=true` is set.

   ```bash
   (cd ./dist && zip -r ../ktl-docent-m365.zip ktl-docent-m365)
   ATK_FRONTIER=true atk add skill --from ./ktl-docent-m365.zip -i false
   ```

4. Run `atk validate`, `atk provision` and `atk preview`.

Custom skills are in preview. Your tenant must be in the Frontier program, and an agent cannot have both skills and embedded files yet.

## Keep it current

The snapshot does not update itself. Rebuild and provision again after each release that changes the bundle.

## Why only the docent

The other three skills need a repository and a shell. The curator could follow if two things existed: a [domain schema](../skills/ktl-curator/references/domain-schemas.md) for Microsoft Entra identities, and an action that lets the agent write to SharePoint.

## Change the instructions

Edit [skill-template.md](skill-template.md). It is not named `SKILL.md`, so installers don't list it as a skill. Its trust labels must match ktl-docent's, and the repository checks enforce that.
