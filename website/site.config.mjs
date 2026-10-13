// The site's addresses and the order of its sidebar, in one place.
// astro.config.mjs and scripts/sync.mjs both read this file.
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, statSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const REPO = "noelmcloughlin/knowledge-trust-ladder";
export const REPO_URL = `https://github.com/${REPO}`;

// A project site under the owner's GitHub Pages domain. A custom domain
// would change SITE, empty BASE, and need the sync to write public/CNAME.
export const SITE = "https://noelmcloughlin.github.io";
export const BASE = "/knowledge-trust-ladder";
export const SITE_URL = SITE + BASE;

export const SITE_DIR = dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = resolve(SITE_DIR, "..");
export const BUNDLE_DIR = resolve(REPO_ROOT, ".lokf", "knowledge");

// Links to repository files name the commit the site was built from, so a
// reader lands on the text the page was rendered from.
export const REF = (() => {
  if (process.env.GITHUB_SHA) return process.env.GITHUB_SHA;
  try {
    return execFileSync("git", ["-C", REPO_ROOT, "rev-parse", "HEAD"], { encoding: "utf8" }).trim();
  } catch {
    return "main";
  }
})();

// Every page under docs/ has a place here. The sync stops with an error
// when a page has none, so a new page cannot go missing from the sidebar.
export const DOCS_GROUPS = [
  { label: "Guides", pages: ["install", "obsidian", "m365", "skills-repositories"] },
  {
    label: "Architecture",
    pages: [
      "architecture",
      "for-the-curious",
      "context-layer",
      "context-layer-technology",
      "three-lines",
      "three-lines-critics",
      "wikiskill",
      "skillwiki",
    ],
  },
  { label: "Maintaining", pages: ["releasing", "signing-commits", "threat-model", "repository-layout"] },
  { label: "Captured sessions", pages: ["examples/docent", "examples/curator", "examples/prose"] },
];

/** The bundle's concept groups: its top-level folders, in name order. */
export function bundleGroups() {
  return readdirSync(BUNDLE_DIR)
    .filter((name) => !name.startsWith(".") && statSync(resolve(BUNDLE_DIR, name)).isDirectory())
    .sort();
}

/** A group's folder name as words, so young-readers reads "Young readers". */
export function groupLabel(group) {
  const words = group.replace(/[-_]+/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** Every concept's ID: its path in the bundle without `.md`, index and log files left out. */
export function conceptIds() {
  const ids = [];
  const walk = (dir, prefix) => {
    for (const name of readdirSync(dir).sort()) {
      if (name.startsWith(".")) continue;
      const full = resolve(dir, name);
      if (statSync(full).isDirectory()) walk(full, prefix + name + "/");
      else if (name.endsWith(".md") && name !== "index.md" && !(prefix === "" && name === "log.md"))
        ids.push(prefix + name.slice(0, -3));
    }
  };
  if (existsSync(BUNDLE_DIR)) walk(BUNDLE_DIR, "");
  return ids;
}
