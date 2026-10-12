// Writes the site's generated sources from the repository before every
// build, so that no page is written twice. Nothing it writes is committed;
// website/.gitignore lists each place:
//
//   src/content/docs/  a page for the README, each docs/ page and each concept
//   src/generated/     the logo, for the header and the home page;
//                      health.json, the numbers the health page charts; and
//                      CHANGELOG.md, which the releases section reads
//   public/            the figures, llms.txt, and under knowledge/ the four
//                      files `lokf export` writes, every bundle file as it is
//                      in the repository, and each concept's JSON-LD
//
// It runs two programs the repository already has: the lokf toolkit's
// `export`, from the sidecar's own environment, and knowledge-report.sh,
// whose labels the concept pages show, so the site never derives a label a
// second way.
import { execFileSync, spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { parse as parseYaml } from "yaml";
import {
  BASE,
  BUNDLE_DIR,
  DOCS_GROUPS,
  REF,
  REPO_ROOT,
  REPO_URL,
  SITE_URL,
  SITE_DIR,
  bundleGroups,
  conceptIds,
  groupLabel,
} from "../site.config.mjs";
import { rewriteUrl } from "./routes.mjs";

const CONTENT = resolve(SITE_DIR, "src", "content", "docs");
const GENERATED = resolve(SITE_DIR, "src", "generated");
const PUBLIC = resolve(SITE_DIR, "public");
const PUBLIC_KNOWLEDGE = resolve(PUBLIC, "knowledge");
const REPORT = resolve(REPO_ROOT, ".lokf", "scripts", "knowledge-report.sh");

const read = (path) => readFileSync(path, "utf8");
const repoFile = (rel) => read(resolve(REPO_ROOT, rel));

function write(path, text) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, text);
}

// JSON is YAML, so the frontmatter needs no YAML writer.
function page(path, frontmatter, body) {
  write(path, `---\n${JSON.stringify(frontmatter, null, 2)}\n---\n\n${body.trim()}\n`);
}

// ---------------------------------------------------------------------------
// Markdown helpers. Each one leaves fenced code alone.
// ---------------------------------------------------------------------------

/** Call fn(line) on every line outside a fenced code block; fn returns the replacement line(s). */
function mapProse(text, fn) {
  const out = [];
  let fence = null;
  for (const line of text.split("\n")) {
    const m = line.match(/^\s*(`{3,}|~{3,})/);
    if (fence) {
      if (m && m[1][0] === fence[0] && m[1].length >= fence.length) fence = null;
      out.push(line);
    } else if (m) {
      fence = m[1];
      out.push(line);
    } else {
      const r = fn(line);
      if (Array.isArray(r)) out.push(...r);
      else if (r !== null) out.push(r);
    }
  }
  return out.join("\n");
}

function splitFrontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { data: {}, body: text };
  return { data: parseYaml(m[1]) ?? {}, body: text.slice(m[0].length) };
}

/** The first `# ` heading as a plain title, and the text without it. */
function takeTitle(body) {
  let title = null;
  const rest = mapProse(body, (line) => {
    if (title === null && /^# /.test(line)) {
      title = plain(line.slice(2));
      return null;
    }
    return line;
  });
  return { title, body: rest };
}

function hasH1(body) {
  let found = false;
  mapProse(body, (line) => {
    if (/^# /.test(line)) found = true;
    return line;
  });
  return found;
}

function demoteHeadings(body) {
  return mapProse(body, (line) => (/^#{1,5} /.test(line) ? "#" + line : line));
}

/** Markdown inline syntax stripped to its words, for titles and descriptions. */
function plain(md) {
  return md
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/(\*\*|__)(.*?)\1/g, "$2")
    .replace(/(^|[^\w*])[*_]([^*_]+)[*_](?=[^\w*]|$)/g, "$1$2")
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/** The first sentence of the first paragraph, or of the first note, as a page description. */
function describe(body) {
  const para = body
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .find((p) => p && !/^(#|<|:::|```|~~~|\||[-*] |\d+\. )/.test(p.replace(/^>\s*(\[![A-Z]+\]\s*)?/gm, "")));
  if (!para) return undefined;
  const text = plain(para.replace(/^>\s?(\[![A-Z]+\]\s*)?/gm, ""));
  const sentence = text.match(/^.+?[.!?](?=\s|$)/);
  return (sentence ? sentence[0] : text).slice(0, 300);
}

const ALERTS = { NOTE: "note", TIP: "tip", IMPORTANT: "note", WARNING: "caution", CAUTION: "danger" };

/** GitHub's `> [!NOTE]` alerts become Starlight's `:::note` asides; fenced code is left alone. */
function alertsToAsides(body) {
  const segments = [];
  let fence = null;
  let buf = [];
  for (const line of body.split("\n")) {
    const m = line.match(/^\s*(`{3,}|~{3,})/);
    if (fence) {
      buf.push(line);
      if (m && m[1][0] === fence[0] && m[1].length >= fence.length) {
        segments.push({ code: true, text: buf.join("\n") });
        buf = [];
        fence = null;
      }
    } else if (m) {
      if (buf.length) segments.push({ code: false, text: buf.join("\n") });
      buf = [line];
      fence = m[1];
    } else {
      buf.push(line);
    }
  }
  if (buf.length) segments.push({ code: Boolean(fence), text: buf.join("\n") });
  return segments.map((s) => (s.code ? s.text : asidesInProse(s.text))).join("\n");
}

function asidesInProse(text) {
  const out = [];
  let open = null;
  const close = () => {
    if (open) out.push(":::", "");
    open = null;
  };
  for (const line of text.split("\n")) {
    const start = line.match(/^>\s*\[!([A-Z]+)\]\s*$/);
    if (start && ALERTS[start[1]]) {
      close();
      open = ALERTS[start[1]];
      out.push("", `:::${open}`);
    } else if (open && /^>/.test(line)) {
      out.push(line.replace(/^>\s?/, ""));
    } else {
      close();
      out.push(line);
    }
  }
  close();
  return out.join("\n");
}

/**
 * A `<picture>` that swaps in a dimmed figure for a dark system theme becomes
 * two images, one shown in each of Starlight's themes, so the figure follows
 * the site's theme switch rather than the system's. The theme's class goes
 * on a wrapper, so the zoom button image zoom adds beside each image is
 * hidden with it, and a keyboard or a screen reader meets one per figure.
 */
function picturesToThemedImages(body) {
  return body.replace(/<picture>([\s\S]*?)<\/picture>/g, (whole, inner) => {
    const dark = inner.match(/<source\b[^>]*media="\(prefers-color-scheme:\s*dark\)"[^>]*srcset="([^"]+)"/);
    const img = inner.match(/<img\b([^>]*?)\s*\/?>/);
    if (!dark || !img) return whole;
    const attrs = img[1].replace(/\s+class="[^"]*"/, "");
    const darkAttrs = attrs.replace(/\bsrc="[^"]*"/, `src="${dark[1]}"`);
    return `<span class="dark:sl-hidden"><img${attrs} /></span><span class="light:sl-hidden"><img${darkAttrs} /></span>`;
  });
}

const prepare = (body) => picturesToThemedImages(alertsToAsides(body));

// ---------------------------------------------------------------------------
// The bundle, as the toolkit and the report script see it.
// ---------------------------------------------------------------------------

function lokfExport() {
  mkdirSync(PUBLIC_KNOWLEDGE, { recursive: true });
  execFileSync(
    "uv",
    [
      "run",
      "--project",
      resolve(REPO_ROOT, ".lokf"),
      "--frozen",
      "--quiet",
      "lokf",
      "export",
      BUNDLE_DIR,
      "--out-dir",
      PUBLIC_KNOWLEDGE,
      "--source-base",
      `${REPO_URL}/blob/${REF}/.lokf/knowledge`,
    ],
    { stdio: "inherit" },
  );
  return {
    graph: JSON.parse(read(resolve(PUBLIC_KNOWLEDGE, "graph.json"))),
    jsonld: JSON.parse(read(resolve(PUBLIC_KNOWLEDGE, "concepts.jsonld"))),
  };
}

function report(...args) {
  const run = spawnSync("bash", [REPORT, "--root", REPO_ROOT, ...args], { encoding: "utf8" });
  if (run.error) throw run.error;
  if (run.status !== 0 && !run.stdout) {
    throw new Error(`knowledge-report.sh ${args.join(" ")} failed: ${run.stderr}`);
  }
  return run.stdout.trimEnd();
}

/** knowledge-report.sh labels: "- Title (group/name.md) - label, label". */
function readLabels() {
  const labels = new Map();
  for (const line of report("labels").split("\n")) {
    const m = line.match(/^- (.*) \(([^()]+\.md)\) - (.*)$/);
    if (m) labels.set(m[2].replace(/\.md$/, ""), m[3]);
  }
  return labels;
}

function toneOf(label) {
  if (label.startsWith("retired")) return "retired";
  if (label.startsWith("confirmed by a person")) return "person";
  if (label.startsWith("edited since a person")) return "edited";
  if (label.startsWith("checked by automation")) return "automation";
  return "nobody";
}
// The ladder, top first; src/trust.ts words each state in the same order.
const TONE_ORDER = ["person", "edited", "automation", "nobody", "retired"];

/** A relation slot's name as words, so derivedFrom reads "Derived from". */
function slotName(slot) {
  const words = slot.replace(/([a-z])([A-Z])/g, "$1 $2").replace(/_/g, " ").toLowerCase();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function githubFile(repoPath) {
  let kind = "blob";
  try {
    if (statSync(resolve(REPO_ROOT, repoPath)).isDirectory()) kind = "tree";
  } catch {
    /* a source that is gone still gets its address */
  }
  return `${REPO_URL}/${kind}/${REF}/${repoPath}`;
}

// The page head carries the concept as JSON-LD. Escaping <, > and & keeps a
// field value such as "</script>" from ending the block; \uXXXX is still JSON.
const scriptSafe = (doc) =>
  JSON.stringify(doc).replace(/</g, "\\u003c").replace(/>/g, "\\u003e").replace(/&/g, "\\u0026");

function buildConcepts(exported, labels) {
  const context = exported.jsonld["@context"];
  const docs = new Map(exported.jsonld["@graph"].map((d) => [d.id ?? d["@id"], d]));
  const nodes = new Map(exported.graph.nodes.map((n) => [n.data.id, n.data]));
  const edges = exported.graph.edges.map((e) => e.data);
  const root = splitFrontmatter(read(resolve(BUNDLE_DIR, "index.md"))).data;
  const baseIri = root.base_iri ?? "";

  const concepts = conceptIds().map((id) => {
    const text = read(resolve(BUNDLE_DIR, `${id}.md`));
    const { data, body } = splitFrontmatter(text);
    const iri = data.id ?? baseIri + id;
    const label = labels.get(id) ?? "nobody has checked this yet";
    return { id, iri, data, body, text, label, tone: toneOf(label), title: String(data.title ?? id) };
  });
  const byIri = new Map(concepts.map((c) => [c.iri, c]));
  const linkTo = (iri) => {
    const c = byIri.get(iri);
    if (c) return { text: c.title, href: `${BASE}/knowledge/${c.id}/`, tone: c.tone };
    const node = nodes.get(iri);
    if (node?.concept_id) return { text: node.label ?? iri, href: `${BASE}/knowledge/${node.concept_id}/` };
    return { text: iri, href: iri };
  };

  for (const c of concepts) {
    const out = new Map();
    for (const e of edges.filter((e) => e.source === c.iri)) {
      const name = slotName(e.slot ?? e.predicate);
      if (!out.has(name)) out.set(name, []);
      out.get(name).push(linkTo(e.target));
    }
    const sources = (Array.isArray(c.data.sources) ? c.data.sources : [])
      .map((s) => (typeof s === "string" ? s : s.resource ?? s.url ?? s.id))
      .filter(Boolean)
      .map(String);
    if (sources.length === 0 && c.data.resource) sources.push(String(c.data.resource));
    const event = (e) => ({ by: String(e.by ?? ""), at: String(e.at ?? ""), ...(e.note ? { note: String(e.note) } : {}) });

    c.record = {
      id: c.id,
      iri: c.iri,
      type: String(c.data.type ?? "Concept"),
      group: c.id.includes("/") ? c.id.split("/")[0] : "",
      ...(c.data.status ? { status: String(c.data.status) } : {}),
      label: c.label,
      tone: c.tone,
      ...(c.data.definition ? { definition: String(c.data.definition) } : {}),
      ...(c.data.stale_after ? { reviewBy: String(c.data.stale_after) } : {}),
      tags: (Array.isArray(c.data.tags) ? c.data.tags : []).map(String),
      ...(c.data.generated ? { generated: event(c.data.generated) } : {}),
      verified: (Array.isArray(c.data.verified) ? c.data.verified : []).map(event),
      sources: sources.map((s) => {
        if (/^https?:/.test(s)) return { text: s, href: s };
        const path = s.replace(/^\.\/?/, "").replace(/\/$/, "");
        if (path === "") return { text: "the whole repository", href: `${REPO_URL}/tree/${REF}` };
        return { text: s, href: githubFile(path) };
      }),
      relations: [...out].map(([name, targets]) => ({
        name,
        targets: targets.sort((a, b) => a.text.localeCompare(b.text)),
      })),
      incoming: edges
        .filter((e) => e.target === c.iri && byIri.has(e.source))
        .map((e) => ({ name: slotName(e.slot ?? e.predicate).toLowerCase(), from: linkTo(e.source) }))
        .sort((a, b) => a.from.text.localeCompare(b.from.text)),
      files: {
        markdown: `${BASE}/knowledge/${c.id}.md`,
        jsonld: `${BASE}/knowledge/${c.id}.jsonld`,
        github: githubFile(`.lokf/knowledge/${c.id}.md`),
      },
    };

    const doc = docs.get(c.iri);
    c.jsonld = doc ? { "@context": context, ...doc } : null;
  }
  return { concepts, root, context };
}

// ---------------------------------------------------------------------------
// Pages.
// ---------------------------------------------------------------------------

function writeConceptPages(concepts) {
  const byGroup = new Map();
  for (const c of concepts) {
    const g = c.record.group;
    if (!byGroup.has(g)) byGroup.set(g, []);
    byGroup.get(g).push(c);
  }
  for (const list of byGroup.values()) list.sort((a, b) => a.title.localeCompare(b.title));

  for (const c of concepts) {
    const order = byGroup.get(c.record.group).indexOf(c) + 1;
    const head = [
      { tag: "link", attrs: { rel: "alternate", type: "text/markdown", href: c.record.files.markdown } },
    ];
    if (c.jsonld) {
      const { body: _body, ...summary } = c.jsonld;
      head.push(
        { tag: "link", attrs: { rel: "alternate", type: "application/ld+json", href: c.record.files.jsonld } },
        { tag: "script", attrs: { type: "application/ld+json" }, content: scriptSafe(summary) },
      );
      write(resolve(PUBLIC_KNOWLEDGE, `${c.id}.jsonld`), JSON.stringify(c.jsonld, null, 2) + "\n");
    }
    page(
      resolve(CONTENT, "knowledge", `${c.id}.md`),
      {
        title: c.title,
        ...(c.data.description ? { description: String(c.data.description) } : {}),
        ktlSource: `.lokf/knowledge/${c.id}.md`,
        ktlShiftHeadings: hasH1(c.body),
        editUrl: false,
        // The sidebar entry carries the concept's trust: catalogue.css draws a
        // dot from the tone, and the label is its tooltip.
        sidebar: { order, attrs: { "data-ktl-tone": c.tone, title: c.label } },
        head,
        lokf: c.record,
      },
      c.body,
    );
  }
  return byGroup;
}

const labelSpan = (c) => `<span class="ktl-label ktl-label--${c.tone}">${c.label}</span>`;

function writeGroupPages(byGroup) {
  for (const group of bundleGroups()) {
    const list = byGroup.get(group) ?? [];
    const items = list.map(
      (c) => `- [${c.title}](${BASE}/knowledge/${c.id}/) ${labelSpan(c)}\\\n  ${String(c.data.description ?? "")}`,
    );
    page(
      resolve(CONTENT, "knowledge", group, "index.md"),
      {
        title: groupLabel(group),
        description: `The concepts in the knowledge bundle's ${group} folder, with how far each has been checked.`,
        editUrl: false,
        sidebar: { label: "Overview", order: 0 },
      },
      `<div class="ktl-list">\n\n${items.join("\n\n")}\n\n</div>`,
    );
  }
}

function parseHealth(line) {
  return line
    .split(" · ")
    .map((part) => part.match(/^(.+?):\s*(.+)$/))
    .filter(Boolean)
    .map((m) => [m[1], m[2]]);
}

function writeOverview(root, concepts, health) {
  const text = read(resolve(BUNDLE_DIR, "index.md"));
  const { body } = splitFrontmatter(text);
  const { body: rest } = takeTitle(body);
  const [intro, ...after] = rest.trim().split(/\n(?=# )/);
  const k = `${BASE}/knowledge`;
  const license = root.license ? `[${root.license}](${root.license})` : "not stated";
  const publisher = root.publisher?.name ?? root.publisher?.id ?? "not stated";
  const facts = [
    "| The root file declares | |",
    "| --- | --- |",
    `| Base IRI | \`${root.base_iri ?? ""}\` |`,
    `| JSON-LD context | \`${root.context ?? ""}\` |`,
    `| Licence | ${license} |`,
    `| Publisher | ${publisher} |`,
    `| Concepts | ${concepts.length} |`,
  ].join("\n");
  const healthList = parseHealth(health)
    .map(([k2, v]) => `- ${k2}: ${v}`)
    .join("\n");
  const files = [
    `- [concepts.jsonld](${k}/concepts.jsonld): every concept's frontmatter and body under one JSON-LD context.`,
    `- [graph.nt](${k}/graph.nt): the whole bundle as N-Triples.`,
    `- [graph.json](${k}/graph.json): the typed relations as cytoscape.js elements, which the [knowledge graph](${BASE}/graph/) draws.`,
    `- [datasets.jsonld](${k}/datasets.jsonld): a schema.org Dataset description for each Dataset or Table concept.`,
    `- [index.md](${k}/index.md): the bundle's root file, which declares the header above.`,
    `- Each concept page links the concept's own Markdown file and its JSON-LD, at the concept's path with \`.md\` or \`.jsonld\` added.`,
    `- The bundle as it stood at each release is a zip on the [releases page](${REPO_URL}/releases).`,
  ].join("\n");
  const generated = [
    intro.trim(),
    facts,
    `# How far it has been checked\n\nThe [bundle health](${BASE}/health/) page gives each concept's label. The counts, computed from frontmatter when the site was built:\n\n${healthList}`,
    `# Files\n\n${files}`,
    `# Contents`,
    after.map((s) => s.replace(/^# /, "## ")).join("\n"),
  ].join("\n\n");
  page(
    resolve(CONTENT, "knowledge", "index.md"),
    {
      title: String(root.title ?? "Knowledge bundle"),
      ...(root.description ? { description: String(root.description) } : {}),
      ktlSource: ".lokf/knowledge/index.md",
      editUrl: false,
      head: [
        { tag: "link", attrs: { rel: "alternate", type: "application/ld+json", href: `${k}/concepts.jsonld` } },
        { tag: "link", attrs: { rel: "alternate", type: "application/n-triples", href: `${k}/graph.nt` } },
      ],
    },
    demoteHeadings(generated),
  );
}

function writeLog() {
  const { body } = splitFrontmatter(read(resolve(BUNDLE_DIR, "log.md")));
  const { body: rest } = takeTitle(body);
  page(
    resolve(CONTENT, "knowledge", "log.md"),
    {
      title: "Bundle log",
      description: "What changed in the knowledge bundle, newest first, as the bundle's log.md records it.",
      ktlSource: ".lokf/knowledge/log.md",
      ktlShiftHeadings: hasH1(rest),
      editUrl: false,
    },
    rest,
  );
}

// The health page is an Astro page, src/pages/health.astro, which charts
// these numbers; the sync only gathers them.
function writeHealth(concepts, health, full) {
  const count = (list) => Object.fromEntries(TONE_ORDER.map((t) => [t, list.filter((c) => c.tone === t).length]));
  const groups = bundleGroups().map((group) => {
    const list = concepts.filter((c) => c.record.group === group);
    return { group, label: groupLabel(group), href: `${BASE}/knowledge/${group}/`, total: list.length, ...count(list) };
  });
  const sorted = [...concepts].sort(
    (a, b) => TONE_ORDER.indexOf(a.tone) - TONE_ORDER.indexOf(b.tone) || a.title.localeCompare(b.title),
  );
  const data = {
    line: parseHealth(health),
    total: concepts.length,
    counts: count(concepts),
    groups,
    concepts: sorted.map((c) => ({
      title: c.title,
      href: `${BASE}/knowledge/${c.id}/`,
      group: groupLabel(c.record.group),
      label: c.label,
      tone: c.tone,
    })),
    report: full,
  };
  write(resolve(GENERATED, "health.json"), JSON.stringify(data, null, 2) + "\n");
}

function writeDocs() {
  const placed = new Set(DOCS_GROUPS.flatMap((g) => g.pages));
  const found = [];
  const walk = (dir, prefix) => {
    for (const name of readdirSync(dir).sort()) {
      const full = resolve(dir, name);
      if (statSync(full).isDirectory()) walk(full, prefix + name + "/");
      else if (name.endsWith(".md")) found.push(prefix + name.slice(0, -3));
    }
  };
  walk(resolve(REPO_ROOT, "docs"), "");
  const missing = found.filter((p) => !placed.has(p));
  const gone = [...placed].filter((p) => !found.includes(p));
  if (missing.length || gone.length) {
    throw new Error(
      `site.config.mjs DOCS_GROUPS is out of step with docs/: ` +
        (missing.length ? `not placed: ${missing.join(", ")}. ` : "") +
        (gone.length ? `placed but missing: ${gone.join(", ")}.` : ""),
    );
  }
  const docs = [];
  for (const name of found) {
    const source = `docs/${name}.md`;
    const { title, body } = takeTitle(repoFile(source));
    const description = describe(body);
    docs.push({ name, title: title ?? name, description });
    page(
      resolve(CONTENT, "docs", `${name}.md`),
      {
        title: title ?? name,
        ...(description ? { description } : {}),
        ktlSource: source,
        editUrl: `${REPO_URL}/edit/main/${source}`,
      },
      prepare(body),
    );
  }
  const order = DOCS_GROUPS.flatMap((g) => g.pages);
  return docs.sort((a, b) => order.indexOf(a.name) - order.indexOf(b.name));
}

function writeReadmes(tagline) {
  // The home page: the README under a hero, which takes the README's logo
  // and its bold summary line, so neither shows twice.
  let readme = repoFile("README.md").replace(/<picture>[\s\S]*?<\/picture>\s*/, "");
  readme = takeTitle(readme).body;
  readme = readme.replace(/^\*\*(.+)\*\*\s*$/m, (_, line) => {
    tagline.text = plain(line);
    return "";
  });
  page(
    resolve(CONTENT, "index.md"),
    {
      title: "Knowledge Trust Ladder",
      description: tagline.text,
      template: "splash",
      hero: {
        tagline: tagline.text,
        image: { light: "../../generated/logo-light.svg", dark: "../../generated/logo-dark.svg", alt: "" },
        actions: [
          { text: "Quick start", link: "#quick-start", icon: "right-arrow" },
          { text: "Browse the bundle", link: `${BASE}/knowledge/`, variant: "secondary" },
          { text: "GitHub", link: REPO_URL, icon: "external", variant: "minimal" },
        ],
      },
      ktlSource: "README.md",
      editUrl: `${REPO_URL}/edit/main/README.md`,
    },
    prepare(readme),
  );

  const simple = takeTitle(repoFile("README.en-simple.md"));
  const description = describe(simple.body);
  page(
    resolve(CONTENT, "simple.md"),
    {
      title: simple.title ?? "Knowledge Trust Ladder, in short",
      ...(description ? { description } : {}),
      ktlSource: "README.en-simple.md",
      editUrl: `${REPO_URL}/edit/main/README.en-simple.md`,
    },
    prepare(simple.body),
  );
}

function writeLlmsTxt(docs, concepts) {
  const repoLlms = repoFile("llms.txt");
  const summary = (repoLlms.match(/^> (.+)$/m) ?? [, "Agent Skills that keep a repository's knowledge as a LOKF bundle."])[1];
  const lines = [
    "# Knowledge Trust Ladder",
    "",
    `> ${summary}`,
    "",
    `This site is built from ${REPO_URL}: its README, its docs/ pages and its LOKF knowledge bundle. Each concept below links its own Markdown file, the file as it is in the repository, followed by the label that says how far it has been checked. A concept marked \`status: draft\` has not yet been confirmed by a person; one with a \`human:\` entry under \`verified\` has. Weigh them accordingly.`,
    "",
    "## Docs",
    "",
    ...docs.map((d) => `- [${d.title}](${SITE_URL}/docs/${d.name}/)${d.description ? `: ${d.description}` : ""}`),
    "",
    "## Knowledge bundle",
    "",
    ...[...concepts]
      .sort((a, b) => a.id.localeCompare(b.id))
      .map((c) => `- [${c.title}](${SITE_URL}/knowledge/${c.id}.md): ${String(c.data.description ?? "")} (${c.label})`),
    "",
    "## Optional",
    "",
    `- [concepts.jsonld](${SITE_URL}/knowledge/concepts.jsonld): every concept's frontmatter and body under one JSON-LD context`,
    `- [graph.nt](${SITE_URL}/knowledge/graph.nt): the whole bundle as N-Triples`,
    `- [README](${SITE_URL}/): what Knowledge Trust Ladder is, and how to install it`,
    "",
  ];
  write(resolve(PUBLIC, "llms.txt"), lines.join("\n"));
}

/** Every file of the bundle as it is in the repository, so `<concept>.md` sits beside its page. */
function copyBundleFiles() {
  const walk = (dir) => {
    for (const name of readdirSync(dir)) {
      if (name.startsWith(".")) continue;
      const full = resolve(dir, name);
      if (statSync(full).isDirectory()) walk(full);
      else if (name.endsWith(".md")) {
        const dest = resolve(PUBLIC_KNOWLEDGE, relative(BUNDLE_DIR, full));
        mkdirSync(dirname(dest), { recursive: true });
        cpSync(full, dest);
      }
    }
  };
  walk(BUNDLE_DIR);
}

/**
 * The releases section's copy of CHANGELOG.md. Its version headings lose
 * their brackets, so each release page is titled with the bare version and
 * starlight-changelogs skips `## Unreleased`, which it knows only unbracketed.
 * Its links to repository files point at their pages, since a release page
 * has no source file for the Markdown plugin to resolve them from.
 */
function writeChangelog() {
  const text = mapProse(repoFile("CHANGELOG.md"), (line) =>
    line
      .replace(/^## \[([^\]]+)\]/, "## $1")
      .replace(/\]\(([^)\s]+)\)/g, (_, url) => `](${rewriteUrl("CHANGELOG.md", url)})`),
  );
  write(resolve(GENERATED, "CHANGELOG.md"), text);
}

function copyAssets() {
  cpSync(resolve(REPO_ROOT, ".assets"), resolve(PUBLIC, "assets"), { recursive: true });
  mkdirSync(GENERATED, { recursive: true });
  cpSync(resolve(REPO_ROOT, ".assets", "knowledge-trust-ladder-logo.svg"), resolve(GENERATED, "logo-light.svg"));
  cpSync(resolve(REPO_ROOT, ".assets", "knowledge-trust-ladder-logo-dimmed.svg"), resolve(GENERATED, "logo-dark.svg"));
  cpSync(resolve(REPO_ROOT, ".assets", "knowledge-trust-ladder-logo.svg"), resolve(PUBLIC, "favicon.svg"));
}

// ---------------------------------------------------------------------------

for (const dir of [CONTENT, GENERATED, PUBLIC]) {
  if (!dir.startsWith(SITE_DIR + "/")) throw new Error(`refusing to clear ${dir}`);
  rmSync(dir, { recursive: true, force: true });
}

if (!existsSync(resolve(BUNDLE_DIR, "index.md"))) throw new Error(`no bundle at ${BUNDLE_DIR}`);
const exported = lokfExport();
const labels = readLabels();
const health = report("health");
const full = report();
const { concepts, root } = buildConcepts(exported, labels);

copyAssets();
copyBundleFiles();
const byGroup = writeConceptPages(concepts);
writeGroupPages(byGroup);
writeOverview(root, concepts, health);
writeLog();
writeHealth(concepts, health, full);
const docs = writeDocs();
writeReadmes({ text: "" });
writeLlmsTxt(docs, concepts);
writeChangelog();

console.log(
  `sync: ${concepts.length} concept pages, ${byGroup.size} groups, ${docs.length} docs pages, ` +
    `${labels.size} labels, built from ${REF.slice(0, 12)}`,
);
