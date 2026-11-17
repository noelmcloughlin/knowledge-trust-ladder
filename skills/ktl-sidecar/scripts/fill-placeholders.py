"""Fills the placeholders of ktl-sidecar's templates in the files named.

    python3 fill-placeholders.py <file> ...

Reads PROJ_NAME, PROJ_DESC, PROJ_SLUG, BASE_IRI, OWNER_NAME, OWNER_SLUG and
TODAY from the environment, and checks each before it writes a file. In
frontmatter and in a .toml file a value is written as the inside of a
double-quoted string. A Markdown body takes it as it is.
"""

import json, os, re, sys
slug = r"[a-z0-9]+(-[a-z0-9]+)*"
shape = {"PROJ_SLUG": slug, "OWNER_SLUG": slug, "TODAY": r"\d{4}-\d{2}-\d{2}", "BASE_IRI": r"https?://[^\s\"\\<>]+/"}
values = {}
for token in ("PROJ_NAME", "PROJ_DESC", "PROJ_SLUG", "BASE_IRI", "OWNER_NAME", "OWNER_SLUG", "TODAY"):
    value = os.environ[token]
    if not value.strip() or not value.isprintable():
        sys.exit(token + ": empty, or a line break or unprintable character")
    if token in shape and not re.fullmatch(shape[token], value):
        sys.exit(token + ": not of the form " + shape[token])
    values[token] = value
def fill(text, quoted):
    def one(found):
        value = values.get(found.group(1), found.group(0))
        return json.dumps(value, ensure_ascii=False)[1:-1] if quoted and found.group(1) in values else value
    return re.sub(r"<([A-Z_]+)>", one, text)
for path in sys.argv[1:]:
    text = open(path, encoding="utf-8").read()
    head, rule, body = "", "", text
    if path.endswith(".md") and text.startswith("---\n"):
        head, rule, body = text.partition("\n---\n")
    text = fill(head, True) + rule + fill(body, path.endswith(".toml"))
    open(path, "w", encoding="utf-8").write(text)
