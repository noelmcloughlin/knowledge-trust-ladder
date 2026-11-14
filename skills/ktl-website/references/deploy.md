# Step 5: the deploy workflow, GitHub Pages, and what collides with it

`templates/github/knowledge-website.yaml` builds the site on every pull request that touches its inputs and publishes the default branch's build to GitHub Pages. This page says what the workflow needs, how Pages is switched on once, and what to do when the repository already publishes Pages another way.

## The two jobs

`build` checks the repository out with its full history, since the health page's "a source moved" lines come from git. It finds the site's folder, `website/` or `ktl-website/`, and runs its `scripts/build.sh`. That script runs `lokf export`, and `gen-doc` for a LinkML schema, from the toolkit `.lokf/uv.lock` pins, then Hugo and Pagefind from the site's own `uv.lock`, then the raw-HTML cleaning and the link check. When `site.toml`'s `browseBuild` runs `just`, which the runner image lacks, a step before the build installs it: the copy `.lokf/uv.lock` pins, checked by hash, or else the same version by name. The job uploads the folder's `dist` as the Pages artifact. It holds `contents: read` and no secret. Third-party code runs in this job only, beside the repository's own: `site.toml` and the files in the site's folder. A private repository should turn harden-runner's egress policy to `block`, with PyPI and the CDN the two libraries come from allowed.

`deploy` runs harden-runner and GitHub's own `deploy-pages` action and nothing else. It holds the `pages: write` and `id-token: write` scopes and runs in the `github-pages` environment, which GitHub limits to the default branch when it creates it. It runs only on the default branch, and only once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Until then the workflow builds on every pull request and deploys nothing, which is the state to leave it in where another publisher exists.

The workflow has no placeholders and names no branch: it reads the repository's default branch from the event.

It runs on a change to the site's folder, the bundle, the README, `docs/`, `.assets/`, the changelog, a schema under `src/` or `.linkml/`, and every Monday from the default branch. A change anywhere else reaches the site with that weekly run, or at once by hand: `gh workflow run knowledge-website.yaml`.

A domain host, which has `knowledge-federation.yaml`, leaves `KNOWLEDGE_WEBSITE_ENABLED` unset: the federation workflow builds the site the same way and deploys it with the workspace beside it, from the release's tag as well as the default branch, so its `github-pages` Environment admits release tags too.

## Switching Pages on

1. Tell Pages once to take its site from Actions: Settings, Pages, Source, GitHub Actions; or `gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow`. A repository whose Pages is already on, from a branch, is switched with `-X PUT` instead.
2. Set the variable on the repository: Settings, Secrets and variables, Actions, Variables, **Repository variables**; or `gh variable set KNOWLEDGE_WEBSITE_ENABLED --body true`, which sets it there. Do not set it on an environment such as `github-pages`: the deploy job's `if:` is read before any environment applies, and it sees only repository and organization variables, so the deploy stays skipped.
3. Push to the default branch, or run the workflow by hand, and open the address `site.toml` names. The first deploy can take a minute to appear.

`uvx ktl gh enable website --run` takes the three steps where Pages is off and no other publisher remains, as ktl-sidecar's [repository-settings.md](../../ktl-sidecar/references/repository-settings.md) says.

A private repository publishes Pages only on a paid plan. The build still runs on every pull request.

## Another publisher

Two publishers overwrite each other's site, so the preflight's `pages` line warns when it finds one: a workflow that names `deploy-pages`, `upload-pages-artifact`, `gh-pages`, `gh-deploy` or `github-pages-deploy-action`, a `CNAME` file, or an `mkdocs.yml` with a `site_url`. Install the workflow, leave the variable unset, and put the choice to the maintainer:

- **Retire the other publisher** and let this workflow publish the whole site. The knowledge site has a home page built from the README and shows the LinkML schema's `gen-doc` pages itself, so it can be the repository's site. For an mkdocs site, the next section lists the steps.
- **Keep the other publisher and serve the bundle inside it.** The four files `lokf export` writes are plain files. A MkDocs or Sphinx build can copy them into its own output from a build step, which makes the repository a producer node without this site.
- **Publish from the `gh-pages` branch under a sub-path**, with an action such as `peaceiris/actions-gh-pages` and a `destination_dir`, and `baseURL` ending in that path. This survives only beside a publisher that does not force-push the branch, and `mkdocs gh-deploy --force` does force-push it.

## Retiring mkdocs

This site replaces an mkdocs site, and every project linkml-project-copier wrote has one. The site keeps the addresses a w3id rule or an old link names: it answers at `/elements/<Term>/` with no setting and sends each to the term's page, whatever its kind, and the redirects in `site.toml` keep the docs pages' old addresses. `docsExclude` keeps gen-doc's `templates-linkml/` and `elements/` off the site without being asked. Step 0 of the skill reads the rest from `mkdocs.yml`, and Step 5b gives the maintainer this list.

The file changes go on a branch with the site, for review. The maintainer takes the Pages and branch steps after that branch is merged, in this order:

1. **Remove both publishers.** In a linkml-project-copier project, `deploy-docs.yaml` pushes `gh-pages` on every push to the default branch, and `test_pages_build.yaml` pushes a preview of each pull request into the same branch. Remove `test_pages_build.yaml` the template's own way, with `copier update --vcs-ref <the _commit in .copier-answers.yml> --data gh_action_docs_preview=false`. Delete `deploy-docs.yaml` by hand, since the template has no question for it.
2. **Remove what only mkdocs used:** `mkdocs.yml`, `docs/js/` (mkdocs' mermaid loader), and the dev dependencies `mkdocs-material`, `mkdocs-mermaid2-plugin`, `mkdocs-pymdownx-material-extras`, `jupyter` and `mknotebooks`, then run `uv lock`. The justfile's `testdoc`, `_serve` and `deploy` recipes belong to the template, and stay. `docs/templates-linkml/` stays too: it holds `gen-doc`'s own templates. copier records a file the project deleted on purpose, and the next update leaves it deleted, unless the template lists the file in `_skip_if_exists`.
3. **Switch Pages from the branch to Actions** (`gh api -X PUT repos/<owner>/<repo>/pages -f build_type=workflow`), set the variable (`gh variable set KNOWLEDGE_WEBSITE_ENABLED --body true`), and run the workflow at once (`gh workflow run knowledge-website.yaml`). Pages serves the old site until the first deployment replaces it.
4. **Check the kept addresses**: run `curl -sI` on a schema page's mkdocs address, such as `<site>/elements/<Class>/`, and on a docs page's, such as `<site>/about/`.
5. **Delete the `gh-pages` branch** last (`git push origin --delete gh-pages`), once the new site answers.

The pull request preview is lost: the workflow builds and checks every pull request, and deploys none. Tell the maintainer once. A preview that pushed into `gh-pages` would race the deployment, so the trade is the right one.

A link to a file mkdocs served beside the pages, such as `schema/<name>.yaml`, goes to the repository at the built commit, as any link to a file that is not a page does.

An `mkdocs.yml` inside `.linkml/`, the linkml-sidecar's copier project, publishes nothing and needs no retirement.

### Reading mkdocs.yml

Step 0 reads `mkdocs.yml` once, by eye, and Step 1 writes what it found into `site.toml`:

- Give each page `nav` names an entry under `[params.redirects]` from its mkdocs address to its file, such as `"about" = "docs/about.md"`, so old links keep working. The schema's pages need none: each answers at `/elements/<Name>/`, where a schema's w3id rules point.
- Add each folder `exclude_docs` names to `docsExclude`.
- Check the Pages address against `site_url`.

## A custom domain, or a user site

Set `baseURL` in `site.toml` to the domain, `https://docs.example.org/`. The domain's DNS and the Pages setting for it stay the repository's own; a deployment from Actions needs no `CNAME` file. A user site, the `<owner>.github.io` repository, sets `baseURL` to `https://<owner>.github.io/`.

## A gitignored `.lokf/`

The workflow builds from the checkout, which lacks a gitignored bundle. Build the site locally (Step 4) and publish the site folder's `dist` by hand, or keep the bundle in git. Skip this step, as the sidecar skips its own Step 5.

## Another forge

The workflow is GitHub Actions. On GitLab, Codeberg, Forgejo, Gitea or another forge, run the same command in that forge's CI, `bash website/scripts/build.sh`, on an image with bash, git and uv, and publish `website/dist` as its pages artifact. GitLab, for example, takes a `public/` folder from a job named `pages`. Links to repository files are built from `params.repo` in GitHub's form, `<repo>/blob/<commit>/<path>`. A forge that spells them another way needs a change to `layouts/_partials/route.html`.

## Behind a proxy

The build fetches from two places. uv installs Hugo and Pagefind from PyPI, so a mirror set for uv (`UV_DEFAULT_INDEX`, and `UV_SYSTEM_CERTS=true` for a root certificate of your own) serves them. Hugo fetches Cytoscape and Mermaid once from a public CDN and checks each against the hash in `hugo.toml`; give `params.vendor.cytoscape.url` and `params.vendor.mermaid.url` a mirror's address in `site.toml`. Nothing is fetched from github.com.

## Keeping the site's tools current

Hugo and Pagefind are pinned in the site folder's `pyproject.toml` and `uv.lock`. A Dependabot entry keeps them current, and the workflow builds each bump on its pull request:

```yaml
  - package-ecosystem: "uv"
    directory: "/website"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(website)"
    groups:
      website:
        patterns: ["*"]
```

A bump moves `pyproject.toml` and `uv.lock` away from the skill's templates, which the preflight's `website` line reports as drift. That drift is expected. The next release of the skill carries the same tools. Hugo changes fast: read its release notes before taking a bump the skill has not taken.
