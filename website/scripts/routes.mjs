// Where a repository path is published. The Markdown plugin and the sync both
// use this, so a link means the same page wherever it is written.
import { statSync } from "node:fs";
import { posix, resolve } from "node:path";
import { BASE, REF, REPO_ROOT, REPO_URL } from "../site.config.mjs";

const ABSOLUTE = /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i;

function isDirectory(repoPath) {
  try {
    return statSync(resolve(REPO_ROOT, repoPath)).isDirectory();
  } catch {
    return false;
  }
}

/** The site path, or the GitHub address, for a path relative to the repository root. */
export function route(repoPath) {
  const p = repoPath.replace(/^knowledge_bundle(?=\/|$)/, ".lokf/knowledge").replace(/\/$/, "");
  if (p === "" || p === "README.md") return `${BASE}/`;
  if (p === "docs/architecture.en-simple.md") return `${BASE}/simple/`;
  if (p === ".lokf/knowledge" || p === ".lokf/knowledge/index.md") return `${BASE}/knowledge/`;
  if (p === ".assets" ) return `${REPO_URL}/tree/${REF}/.assets`;
  let m = p.match(/^docs\/(.+)\.md$/);
  if (m) return `${BASE}/docs/${m[1]}/`;
  m = p.match(/^\.lokf\/knowledge\/(.+)\.md$/);
  if (m) {
    const id = m[1];
    if (id.endsWith("/index")) return `${BASE}/knowledge/${id.slice(0, -"/index".length)}/`;
    return `${BASE}/knowledge/${id}/`;
  }
  m = p.match(/^\.lokf\/knowledge\/([^/]+)$/);
  if (m && isDirectory(p)) return `${BASE}/knowledge/${m[1]}/`;
  if (p.startsWith(".assets/")) return `${BASE}/assets/${p.slice(".assets/".length)}`;
  return `${REPO_URL}/${isDirectory(p) ? "tree" : "blob"}/${REF}/${p}`;
}

/** Rewrite a link written in the file at `fromPath` (repository-relative). */
export function rewriteUrl(fromPath, url) {
  if (!url || ABSOLUTE.test(url) || url.startsWith("#") || url.startsWith("/")) return url;
  const hashAt = url.indexOf("#");
  const pathPart = hashAt < 0 ? url : url.slice(0, hashAt);
  const hash = hashAt < 0 ? "" : url.slice(hashAt);
  if (pathPart === "") return url;
  let decoded = pathPart;
  try {
    decoded = decodeURI(pathPart);
  } catch {
    /* keep it as written */
  }
  const target = posix.normalize(posix.join(posix.dirname(fromPath), decoded));
  if (target.startsWith("..")) return url;
  return route(target === "." ? "" : target) + hash;
}

/** A `srcset` value holds one or more "url descriptor" pairs. */
export function rewriteSrcset(fromPath, value) {
  return value
    .split(",")
    .map((part) => {
      const [u, ...rest] = part.trim().split(/\s+/);
      return [rewriteUrl(fromPath, u), ...rest].join(" ");
    })
    .join(", ");
}

/** Rewrite the src, srcset and href attributes in a fragment of raw HTML. */
export function rewriteHtml(fromPath, html) {
  return html.replace(/\b(src|srcset|href)=("([^"]*)"|'([^']*)')/g, (all, attr, _q, dq, sq) => {
    const value = dq ?? sq;
    const out = attr === "srcset" ? rewriteSrcset(fromPath, value) : rewriteUrl(fromPath, value);
    return `${attr}="${out}"`;
  });
}
