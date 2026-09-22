# The same labels as SPARQL (optional)

For people who run `just lokf-serve` (SPARQL endpoint at `http://127.0.0.1:8000/sparql`, LOKF prefixes preset - no `PREFIX` lines needed). Nothing in the curator skill requires these; the report is computed from frontmatter. They are here because the questions are natural graph questions once the bundle is projected.

> Written from the LOKF schema's declared slot URIs (`verified` ->
> `lokf:verified`, its `by`/`at` -> `prov:wasAssociatedWith` /
> `prov:endedAtTime`; `generated` -> `prov:wasGeneratedBy`; `status` ->
> `schema:creativeWorkStatus`; `stale_after` -> `schema:expires`; `title` ->
> `schema:name`). Check them against your own `just lokf-convert` output
> once - engines differ on date/dateTime comparisons, so dates are compared
> as `YYYY-MM-DD` strings below.

## Nobody has checked this yet

```sparql
SELECT ?c ?title
WHERE { ?c schema:name ?title .
        FILTER NOT EXISTS { ?c lokf:verified ?v } }
ORDER BY ?title
```

## Checked by automation only

```sparql
SELECT ?c ?title
WHERE { ?c schema:name ?title ; lokf:verified ?v .
        FILTER NOT EXISTS { ?c lokf:verified ?h . ?h prov:wasAssociatedWith ?by .
                            FILTER(STRSTARTS(STR(?by), "human:")) } }
ORDER BY ?title
```

## Confirmed by a person (latest confirmation)

```sparql
SELECT ?c ?title (MAX(?at) AS ?lastConfirmed)
WHERE { ?c schema:name ?title ; lokf:verified ?v .
        ?v prov:wasAssociatedWith ?by ; prov:endedAtTime ?at .
        FILTER(STRSTARTS(STR(?by), "human:")) }
GROUP BY ?c ?title
ORDER BY ?lastConfirmed
```

## Edited since a person last confirmed it

```sparql
SELECT ?c ?title ?edited ?lastConfirmed
WHERE {
  ?c schema:name ?title ; prov:wasGeneratedBy ?g . ?g prov:endedAtTime ?edited .
  { SELECT ?c (MAX(?at) AS ?lastConfirmed)
    WHERE { ?c lokf:verified ?v . ?v prov:wasAssociatedWith ?by ; prov:endedAtTime ?at .
            FILTER(STRSTARTS(STR(?by), "human:")) }
    GROUP BY ?c }
  FILTER(STR(?edited) > STR(?lastConfirmed))
}
ORDER BY DESC(?edited)
```

## Past its review date

```sparql
SELECT ?c ?title ?due
WHERE { ?c schema:name ?title ; schema:expires ?due .
        FILTER(SUBSTR(STR(?due), 1, 10) <= SUBSTR(STR(NOW()), 1, 10)) }
ORDER BY ?due
```

## Still a draft / Retired

```sparql
SELECT ?c ?title ?status
WHERE { ?c schema:name ?title ; schema:creativeWorkStatus ?status .
        FILTER(STR(?status) IN ("draft", "deprecated")) }
ORDER BY ?status ?title
```

## Most relied-upon (inbound typed relations)

```sparql
SELECT ?target (COUNT(?s) AS ?reliedOnBy)
WHERE { ?s ?p ?target .
        FILTER(?p IN (dcterms:isPartOf, schema:hasPart, dcterms:references,
                      dcterms:requires, prov:wasDerivedFrom, schema:about,
                      schema:sameAs, dcterms:relation, rdfs:isDefinedBy,
                      dcterms:source)) }
GROUP BY ?target
ORDER BY DESC(?reliedOnBy)
```

Join this with "nobody has checked this yet" to get the report's highest-leverage unchecked concepts.
