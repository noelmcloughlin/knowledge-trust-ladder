# Step 5: the deploy workflow, GitHub Pages, and what collides with it

`templates/github/knowledge-website.yaml` builds the site on every pull request that touches its inputs and publishes the default branch's build to GitHub Pages. This page says what the workflow needs, how Pages is switched on once, and what to do when the repository already publishes Pages another way.

## The two jobs

`build` checks the repository out with its full history, since the health page's "a source moved" lines come from git. It installs the lokf toolkit with `uv sync --locked` in `.lokf/`, and installs the site's packages with `npm ci --ignore-scripts`, so no package runs an install script. It runs `npm run build` (the sync, the build, the link check) with Astro's telemetry off, and uploads `website/dist` as the Pages artifact. It holds `contents: read` and no secret, and third-party code runs there only, beside the repository's own: `site.config.mjs`, the files under `website/`, and the commands that build the schema's pages and the data. A private repository should turn harden-runner's egress policy to `block`, with the package registries allowed.

`deploy` runs harden-runner and GitHub's own `deploy-pages` action and nothing else, with the `pages: write` and `id-token: write` scopes, in the `github-pages` environment, which GitHub limits to the default branch when it creates it. It runs only on the default branch, and only once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Until then the workflow builds on every pull request and deploys nothing, which is the state to leave it in where another publisher exists.

The workflow has no placeholders and names no branch: it reads the repository's default branch from the event.

## The schema's pages and the data

A `SCHEMA` or `BROWSE` folder is never committed, so the sync builds it on every run of the workflow with the command `site.config.mjs` names. When that command starts with `just`, the build job installs `just` first. A command that uses `uv run` installs the project's dependencies from its lock first, which can take minutes for a large project. The workflow also runs on a change to `.linkml/`, a justfile, a `pyproject.toml` or a `uv.lock`, and every Monday from the default branch. A schema or data change anywhere else reaches the site with that weekly run, or at once by hand: `gh workflow run knowledge-website.yaml`.

Datasette Lite fetches each database from the site, which GitHub Pages allows from any origin. It downloads the whole file, and Pages publishes at most 1 GB in all, so a database of a few tens of MB suits it. For larger data, publish Datasette itself elsewhere, with `datasette publish`, and link it from a docs page.

## Switching Pages on

1. Tell Pages once to take its site from Actions: Settings, Pages, Source, GitHub Actions; or `gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow`. A repository whose Pages is already on, from a branch, is switched with `-X PUT` instead.
2. Set the variable on the repository: Settings, Secrets and variables, Actions, Variables, **Repository variables**; or `gh variable set KNOWLEDGE_WEBSITE_ENABLED --body true`, which sets it there. Do not set it on an environment such as `github-pages`: the deploy job's `if:` is read before any environment applies, and it sees only repository and organization variables, so the deploy stays skipped.
3. Push to the default branch, or run the workflow by hand, and open the address `site.config.mjs` names. The first deploy can take a minute to appear.

A private repository publishes Pages only on a paid plan; the build still runs on every pull request.

## Another publisher

Two publishers overwrite each other's site, so the preflight's `pages` line warns when it finds one: a workflow that names `deploy-pages`, `upload-pages-artifact`, `gh-pages`, `gh-deploy` or `github-pages-deploy-action`, a `CNAME` file, or an `mkdocs.yml` with a `site_url`. Install the workflow, leave the variable unset, and put the choice to the maintainer:

- **Retire the other publisher** and let this workflow publish the whole site. The knowledge site has a home page built from the README and shows the LinkML schema's `gen-doc` pages itself, so it can be the repository's site.
- **Keep the other publisher and serve the bundle inside it.** The four files `lokf export` writes are plain files; a MkDocs or Sphinx build can copy them into its own output from a build step, which makes the repository a producer node without this site.
- **Publish from the `gh-pages` branch under a sub-path**, with an action such as `peaceiris/actions-gh-pages` and a `destination_dir`, and `BASE` set to that path. This survives only beside a publisher that does not force-push the branch; `mkdocs gh-deploy --force` does.

## A custom domain, or a user site

Set `CUSTOM_DOMAIN` in `site.config.mjs`: the sync writes `public/CNAME`, `SITE` becomes `https://<domain>` and `BASE` becomes empty. The domain's DNS and the Pages setting for it stay the repository's own. A user site, the `<owner>.github.io` repository, keeps `SITE` and sets `BASE` to `""`.

## A gitignored `.lokf/`

The workflow builds from the checkout, which lacks a gitignored bundle. Build the site locally (Step 4) and publish `website/dist` by hand, or keep the bundle in git. Skip this step, as the sidecar skips its own Step 5.

## Another forge

The workflow is GitHub Actions. On GitLab, Codeberg, Forgejo, Gitea or another forge, run the same commands in that forge's CI (`uv sync --locked` in `.lokf/`, then `npm ci --ignore-scripts` and `npm run build` in `website/`) and publish `website/dist` as its pages artifact. GitLab, for example, takes a `public/` folder from a job named `pages`. Links to repository files still name `github.com`, since `REPO_URL` does; a forge-neutral link is a change to `scripts/routes.mjs`.

## Keeping the site's packages current

The site's npm packages are pinned in `website/package-lock.json`. A Dependabot entry keeps them current, and the workflow builds each bump on its pull request:

```yaml
  - package-ecosystem: "npm"
    directory: "/website"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(website)"
    groups:
      website:
        patterns: ["*"]
```

A bump moves `website/package.json` and the lock away from the skill's templates, which the preflight's `website` line reports as drift. That drift is expected; the next release of the skill carries the same packages.
