#!/usr/bin/env bash
# Writes what Hugo cannot work out for itself into generated/, which is never
# committed: the four files `lokf export` writes, the pages gen-doc writes
# for a LinkML schema, the trust labels and health line knowledge-report.sh
# prints, the repository's tags, and the data when site.toml names it.
# Everything else Hugo reads straight from the repository through the mounts
# in hugo.toml.
# Any step that fails stops the build: a site with no labels would show every
# concept as unchecked.
set -euo pipefail

here=$(cd "$(dirname "$0")/.." && pwd)
root=$(cd "$here/.." && pwd)
out="$here/generated"
repo_url=$(sed -n 's/^repo = "\(.*\)"$/\1/p' "$here/site.toml")
[ -n "$repo_url" ] || { echo "prepare.sh: site.toml has no repo = \"...\" line" >&2; exit 1; }
[ -f "$root/.lokf/knowledge/index.md" ] || { echo "prepare.sh: no .lokf/knowledge/index.md under $root; the ktl-sidecar skill installs the bundle" >&2; exit 1; }
# The commit of the build, or the branch where the folder is not under git.
branch=$(sed -n 's/^branch = "\(.*\)"$/\1/p' "$here/site.toml")
ref=$(git -C "$root" rev-parse HEAD 2>/dev/null || echo "${branch:-main}")

# An SVG is served as a page of its own, so one that holds a script, an event
# handler or a javascript: address would run on the site's address.
if active=$(grep -rlEi --include='*.svg' '<script|<foreignObject|[[:space:]]on[a-z]+[[:space:]]*=|javascript:' "$root/.assets" "$root/docs" "$root/.lokf/knowledge" "$here/static" 2>/dev/null); then
  echo "prepare.sh: these SVG files hold a script, an event handler or a javascript: address, and the site would serve them:" >&2
  echo "$active" >&2
  exit 1
fi

rm -rf "$out"
mkdir -p "$out/knowledge"

# The bundle's own tools: lokf, and the LinkML it is built on.
lokf=(uv run --project "$root/.lokf" --frozen --quiet)

# The domain vocabulary the sidecar's justfile names, so the export carries
# its classes as `just lokf-convert` does.
schema=$(sed -n 's/^schema := "\(.*\)"$/\1/p' "$root/.lokf/justfile" 2>/dev/null || true)
"${lokf[@]}" lokf export ${schema:+--schema "$root/.lokf/$schema"} "$root/.lokf/knowledge" \
  --out-dir "$out/knowledge" \
  --source-base "$repo_url/blob/$ref/.lokf/knowledge"

# A LinkML project's schema, src/<name>/schema/<name>.yaml at the root or in
# the .linkml/ sidecar, the root's first. gen-doc writes a page per class, slot, enumeration
# and type, each kind in a folder of its own, and gen-erdiagram the diagram
# the overview shows. The schema file is copied beside them, with its path in
# the repository. With no schema there is no generated/schema/, and the site
# shows no Schema part.
for model in "$root"/src/*/schema/*.yaml "$root"/.linkml/src/*/schema/*.yaml; do
  name=$(basename "$model" .yaml)
  [ -f "$model" ] && [ "$(basename "${model%/schema/*}")" = "$name" ] || continue
  # gen-doc prints a stray "None" when it ends.
  "${lokf[@]}" gen-doc --subfolder-type-separation --index-name _index -d "$out/schema" "$model" >/dev/null
  "${lokf[@]}" gen-erdiagram --format mermaid "$model" >"$out/schema/diagram.mmd"
  cp "$model" "$out/schema/"
  echo "${model#"$root/"}" >"$out/schema/source.txt"
  break
done

# The data, when site.toml names its folder: each SQLite database in it,
# served under browse/, and its Datasette metadata as metadata.json without
# the plugins' settings, which Datasette Lite never runs and which can hold a
# credential. The folder's own command writes it when it holds no database.
# Nothing else in the folder is served.
browse=$(sed -n 's/^browse = "\(.*\)"$/\1/p' "$here/site.toml")
if [ -n "$browse" ]; then
  build=$(sed -n 's/^browseBuild = "\(.*\)"$/\1/p' "$here/site.toml")
  databases() { find "$root/$browse" -maxdepth 1 -type f \( -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.db' \) 2>/dev/null; }
  if [ -z "$(databases)" ]; then
    [ -n "$build" ] || { echo "prepare.sh: site.toml's browse names $browse, which holds no database, and no browseBuild writes it" >&2; exit 1; }
    echo "prepare.sh: building $browse with \`$build\`"
    (cd "$root" && bash -c "$build")
    [ -n "$(databases)" ] || { echo "prepare.sh: \`$build\` ran, but $browse still holds no database; set browse to the folder it writes" >&2; exit 1; }
  fi
  mkdir -p "$out/browse"
  "${lokf[@]}" python - "$root/$browse" "$out" "$build" <<'PY'
import json, shutil, sys
from pathlib import Path
import yaml

folder, out, build = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
names = sorted(p.name for p in folder.iterdir() if p.is_file())
files = [n for n in names if n.endswith((".sqlite", ".sqlite3", ".db"))]
for name in files:
    for journal in (f"{name}-wal", f"{name}-journal"):
        if (folder / journal).is_file() and (folder / journal).stat().st_size > 0:
            sys.exit(f"prepare.sh: {folder / journal} is not empty: a write to {name} is unfinished or still open, so a copy could be torn")
    shutil.copyfile(folder / name, out / "browse" / name)
found = [n for n in names if n in ("metadata.yaml", "metadata.yml", "metadata.json")]
if len(found) > 1:
    sys.exit(f"prepare.sh: {folder} holds {' and '.join(found)}, and Datasette reads one: keep one")
metadata = None
if found:
    metadata = yaml.safe_load((folder / found[0]).read_text(encoding="utf-8")) or {}
    def bare(part):
        return {k: v for k, v in part.items() if k != "plugins"} if isinstance(part, dict) else part
    metadata = bare(metadata)
    if isinstance(metadata.get("databases"), dict):
        metadata["databases"] = {name: bare(db) for name, db in metadata["databases"].items()}
        for db in metadata["databases"].values():
            if isinstance(db, dict) and isinstance(db.get("tables"), dict):
                db["tables"] = {name: bare(table) for name, table in db["tables"].items()}
    (out / "browse" / "metadata.json").write_text(json.dumps(metadata) + "\n", encoding="utf-8")
listed = []
for name in files:
    stem = name.rsplit(".", 1)[0]
    about = ((metadata or {}).get("databases") or {}).get(stem) or {}
    size = (folder / name).stat().st_size
    listed.append({"file": name, "name": stem, "title": str(about.get("title") or stem), "description": str(about.get("description") or ""),
                   "size": f"{size / 1e6:.1f} MB" if size >= 1e6 else f"{max(1, round(size / 1e3))} kB"})
(out / "browse.json").write_text(json.dumps({"databases": listed, "metadata": bool(found), "build": build}) + "\n", encoding="utf-8")
PY
fi

report="$root/.lokf/scripts/knowledge-report.sh"
bash "$report" --root "$root" labels >"$out/labels.txt"
bash "$report" --root "$root" health >"$out/health.txt"
git -C "$root" tag --list >"$out/tags.txt" 2>/dev/null || : >"$out/tags.txt"

echo "prepare.sh: wrote $(find "$out/knowledge" -type f | wc -l) export files and $(wc -l <"$out/labels.txt") labels to $out"
