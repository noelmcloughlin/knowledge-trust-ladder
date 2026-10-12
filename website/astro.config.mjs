// @ts-check
// The Knowledge Trust Ladder site. Every page is built from a file the
// repository already holds: the README and docs/ become pages, each concept
// in the knowledge bundle becomes a page with its trust label, and the four
// files `lokf export` writes are served beside them. scripts/sync.mjs writes
// the generated sources before every build; nothing it writes is committed.
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { satteri } from "@astrojs/markdown-satteri";
import markdownKtl from "./scripts/markdown-ktl.mjs";
import starlightChangelogs, { makeChangelogsSidebarLinks } from "starlight-changelogs";
import starlightImageZoom from "starlight-image-zoom";
import starlightSidebarTopics from "starlight-sidebar-topics";
import {
  BASE,
  DOCS_GROUPS,
  REPO_URL,
  SITE,
  bundleGroups,
  conceptIds,
  groupLabel,
} from "./site.config.mjs";

export default defineConfig({
  site: SITE,
  base: BASE,
  markdown: {
    processor: satteri({ mdastPlugins: [markdownKtl({ conceptIds: conceptIds() })] }),
  },
  integrations: [
    starlight({
      title: "Knowledge Trust Ladder",
      description:
        "Agent Skills that keep a repository's knowledge as a catalogued LOKF bundle, with the trust in every claim left visible.",
      logo: {
        light: "./src/generated/logo-light.svg",
        dark: "./src/generated/logo-dark.svg",
      },
      social: [{ icon: "github", label: "GitHub", href: REPO_URL }],
      // The two typefaces are self-hosted, so no page calls a font service.
      customCss: [
        "@fontsource-variable/atkinson-hyperlegible-next",
        "@fontsource-variable/source-serif-4",
        "./src/styles/theme.css",
        "./src/styles/catalogue.css",
      ],
      components: {
        PageTitle: "./src/components/PageTitle.astro",
        PageSidebar: "./src/components/PageSidebar.astro",
      },
      // The generated sources are untracked, so git cannot date them; a
      // concept page shows its own `generated` and `verified` times instead.
      lastUpdated: false,
      routeMiddleware: "./src/routeData.ts",
      plugins: [
        // Click a figure to see it at full size: KTL's diagrams are dense at
        // the page's width.
        starlightImageZoom(),
        // A page per release, read from CHANGELOG.md through the sync.
        starlightChangelogs(),
        // The guide, the bundle and the releases each get a sidebar of their
        // own, with a switch between them at its top.
        starlightSidebarTopics(
          [
            {
              label: "Guide",
              link: "/",
              icon: "open-book",
              items: [
                { label: "Home", link: "/" },
                { label: "For readers aged 13 to 18", link: "/simple/" },
                ...DOCS_GROUPS.map((group) => ({
                  label: group.label,
                  items: group.pages.map((page) => `docs/${page}`),
                })),
              ],
            },
            {
              label: "Knowledge bundle",
              link: "/knowledge/",
              icon: "list-format",
              items: [
                { label: "About the bundle", link: "/knowledge/" },
                { label: "Bundle health", link: "/health/" },
                { label: "Knowledge graph", link: "/graph/" },
                ...bundleGroups().map((group) => ({
                  label: groupLabel(group),
                  collapsed: true,
                  items: [{ autogenerate: { directory: `knowledge/${group}` } }],
                })),
                { label: "Bundle log", link: "/knowledge/log/" },
              ],
            },
            {
              label: "Releases",
              id: "releases",
              link: "/changelog/",
              icon: "rocket",
              items: makeChangelogsSidebarLinks([
                { type: "all", base: "changelog", label: "All releases" },
                { type: "recent", base: "changelog", count: 8 },
              ]),
            },
          ],
          // The sidebar lists the eight newest releases; this puts every release
          // page under the Releases topic, the older ones and the comparisons too.
          { topics: { releases: ["/changelog/**"] } },
        ),
      ],
    }),
  ],
});
