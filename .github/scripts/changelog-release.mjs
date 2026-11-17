#!/usr/bin/env node
// Reads and rewrites the "## [Unreleased]" section of this repository's
// CHANGELOG.md for the semantic-release pipeline in
// .github/workflows/semantic-release.yml. Plain Node with no dependencies
// keeps it reviewable in one read, and the project prefers a fixed script to
// an inline command string (see knowledge-librarian.sh).
//
// Usage:
//   node changelog-release.mjs check [version]
//       Exits 1 if "## [Unreleased]" is empty. semantic-release runs it as
//       verifyReleaseCmd, so nothing is released without notes. With a
//       version, an empty section passes when that version is already
//       promoted and waits for publish.yml: a push with nothing to release,
//       such as a docs merge after a feat, still finds the feat since the
//       last tag, and its notes are already written.
//
//   node changelog-release.mjs notes [version]
//       Prints the Unreleased section's body, the release notes when
//       semantic-release runs this as generateNotesCmd. With a version, it
//       also appends `next_version=<version>` to $GITHUB_OUTPUT if that is
//       set, a side channel a caller can read even from a --dry-run. When the
//       section is empty and that version is already promoted, it prints that
//       version's notes instead and appends nothing, so the workflow commits
//       no promotion.
//
//   node changelog-release.mjs promote <version> <date>
//       Retitles "## [Unreleased]" to "## [<version>] - <date>" and puts a
//       new, empty "## [Unreleased]" above it. When the top released section
//       is still pending, with no tag v<its version>, it folds the Unreleased
//       entries into that section instead, subsection by subsection, and
//       gives it the new version and date. So two qualifying pushes between
//       publishes never leave two headings for one release. semantic-release
//       runs it as prepareCmd, never in --dry-run. It appends `released=true`
//       and `version=<version>` to $GITHUB_OUTPUT if that is set.

import { readFileSync, writeFileSync, appendFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const FILE = "CHANGELOG.md";
const HEADING = "## [Unreleased]";
// The heading on a line of its own, whatever ends the line. An entry or a
// preamble may quote the phrase, and a line that holds it in passing is not
// the heading.
const HEADING_LINE = /^## \[Unreleased\][ \t]*\r?$/m;
const RELEASED = /^## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}$/;

function readUnreleased() {
  const text = readFileSync(FILE, "utf8");
  const found = HEADING_LINE.exec(text);
  if (!found) {
    throw new Error(`${FILE} has no "${HEADING}" heading - this pipeline expects one.`);
  }
  const start = found.index;
  const bodyStart = start + found[0].length;
  const next = text.indexOf("\n## [", bodyStart);
  const bodyEnd = next === -1 ? text.length : next;
  return { text, start, bodyStart, body: text.slice(bodyStart, bodyEnd).trim(), end: bodyEnd };
}

// The released section directly under Unreleased, when no tag carries its
// version. publish.yml alone creates tags, so no tag means promoted and not
// yet published.
function pendingSection(text, from) {
  if (from === text.length) return null;
  const lineEnd = text.indexOf("\n", from + 1);
  const heading = text.slice(from + 1, lineEnd === -1 ? text.length : lineEnd);
  const m = RELEASED.exec(heading);
  if (!m) return null;
  let tagged;
  try {
    tagged = execFileSync("git", ["tag", "-l", `v${m[1]}`], { encoding: "utf8", stdio: "pipe" });
  } catch (e) {
    throw new Error(`could not list tags to tell whether ${m[1]} shipped - promote runs inside the repository checkout: ${e.message.split("\n")[0]}`);
  }
  if (tagged.trim()) return null;
  const bodyStart = lineEnd === -1 ? text.length : lineEnd;
  const next = text.indexOf("\n## [", bodyStart);
  const end = next === -1 ? text.length : next;
  return { version: m[1], body: text.slice(bodyStart, end).trim(), end };
}

// A section body as its "### " subsections, blank edges trimmed, so two
// bodies merge by subsection title rather than by concatenation.
function subsections(body) {
  const parts = [];
  let current = { title: null, lines: [] };
  for (const line of body.split("\n")) {
    if (line.startsWith("### ")) {
      parts.push(current);
      current = { title: line, lines: [] };
    } else {
      current.lines.push(line);
    }
  }
  parts.push(current);
  for (const p of parts) {
    while (p.lines.length && !p.lines[0].trim()) p.lines.shift();
    while (p.lines.length && !p.lines[p.lines.length - 1].trim()) p.lines.pop();
  }
  return parts.filter((p) => p.title !== null || p.lines.length);
}

// Keep a Changelog's order for the subsections; a preamble stays first and an
// unlisted title goes last, in the order met.
const ORDER = ["### Added", "### Changed", "### Deprecated", "### Removed", "### Fixed", "### Security"];
const rank = (p) => (p.title === null ? -1 : ORDER.includes(p.title) ? ORDER.indexOf(p.title) : ORDER.length);

// A subsection's lines as entries. A "- " bullet takes the indented and
// blank lines under it, which continue it, so an entry is kept or left out
// whole. Any other line is an entry of its own.
function entries(lines) {
  const found = [];
  for (const line of lines) {
    const last = found[found.length - 1];
    const continues = last && last.bullet && !line.startsWith("- ") && (!line.trim() || /^\s/.test(line));
    if (continues) last.lines.push(line);
    else found.push({ bullet: line.startsWith("- "), lines: [line] });
  }
  return found;
}

// An entry the pending section already holds is left out: a branch stacked
// on another still carries the other's entries under Unreleased after the
// first one's promotion, and folding them again would list each one twice.
// Two entries are the same when the bullet and its continuation are.
function mergeBodies(older, newer) {
  const merged = subsections(older);
  const whole = (e) => e.lines.join("\n").trimEnd();
  const held = new Set(merged.flatMap((m) => entries(m.lines)).filter((e) => e.bullet).map(whole));
  for (const part of subsections(newer)) {
    const all = entries(part.lines);
    const kept = all.filter((e) => !e.bullet || !held.has(whole(e)));
    if (!kept.some((e) => e.bullet) && all.some((e) => e.bullet)) continue;
    const lines = kept.flatMap((e) => e.lines);
    while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
    const same = merged.find((m) => m.title === part.title);
    if (same) same.lines.push(...lines);
    else merged.push({ ...part, lines });
  }
  merged.sort((a, b) => rank(a) - rank(b));
  return merged
    .map((p) => (p.title === null ? p.lines : [p.title, "", ...p.lines]).join("\n"))
    .join("\n\n");
}

function writeOutput(line) {
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, line);
}

// The promoted section that already holds `version`'s notes, when the
// Unreleased section is empty: the case where a push has nothing new to
// describe. Null otherwise, including when the version differs, since then
// something new would release with no notes.
function alreadyPromoted(version) {
  const { text, body, end } = readUnreleased();
  if (body || !version) return null;
  const pending = pendingSection(text, end);
  return pending && pending.version === version ? pending : null;
}

// semantic-release prints a failing command's error with its stack, so also
// write the reason as a GitHub annotation, which the run's summary shows
// on its own line.
function fail(message) {
  if (process.env.GITHUB_ACTIONS) console.log(`::error title=${FILE}::${message}`);
  console.error(message);
  process.exit(1);
}

const [, , cmd, ...args] = process.argv;

switch (cmd) {
  case "check": {
    const [version] = args;
    const { body } = readUnreleased();
    if (!body && alreadyPromoted(version)) {
      console.error(`ok - nothing new since "## [${version}]", which waits for publish.yml.`);
      break;
    }
    if (!body) {
      fail(
        `${FILE}'s "${HEADING}" section is empty. This pipeline only releases what a ` +
          "person or agent has already described there - write it before merging to main."
      );
    }
    console.error(`ok - "${HEADING}" has ${body.length} characters to release.`);
    break;
  }

  case "notes": {
    const [version] = args;
    const { body } = readUnreleased();
    const pending = alreadyPromoted(version);
    if (pending) {
      process.stdout.write(pending.body + "\n");
      break;
    }
    if (version) writeOutput(`next_version=${version}\n`);
    process.stdout.write(body + "\n");
    break;
  }

  case "promote": {
    const [version, date] = args;
    if (!version || !date) {
      console.error("usage: changelog-release.mjs promote <version> <date>");
      process.exit(1);
    }
    const { text, start, bodyStart, body, end } = readUnreleased();
    if (!body) {
      console.error(`${FILE}'s "${HEADING}" section is empty; refusing to promote nothing.`);
      process.exit(1);
    }
    const pending = pendingSection(text, end);
    let promoted;
    if (pending) {
      const section = `${HEADING}\n\n## [${version}] - ${date}\n\n${mergeBodies(pending.body, body)}\n`;
      promoted = text.slice(0, start) + section + text.slice(pending.end);
      console.error(
        `folded "${HEADING}" into the unpublished "## [${pending.version}]" section, ` +
          `now "## [${version}] - ${date}" in ${FILE}`
      );
    } else {
      promoted = `${text.slice(0, start)}${HEADING}\n\n## [${version}] - ${date}${text.slice(bodyStart)}`;
      console.error(`promoted "${HEADING}" to "## [${version}] - ${date}" in ${FILE}`);
    }
    if (promoted === text) {
      throw new Error(`Replacement had no effect - is "${HEADING}" definitely in ${FILE}?`);
    }
    writeFileSync(FILE, promoted);
    writeOutput(`released=true\nversion=${version}\n`);
    break;
  }

  default:
    console.error("usage: changelog-release.mjs <check|notes|promote> ...");
    process.exit(1);
}
