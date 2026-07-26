# AAL-Viz Asset Naming Standard

## File names

```
{category}/{semantic_slug}[.variant].svg
```

| Segment | Rule | Example |
|---------|------|---------|
| category dir | lowercase noun | `authority/`, `graph/nodes/` |
| semantic_slug | `snake_case` or status `SCREAMING` mapped to lower | `observed.svg`, `fail_closed.svg` |
| variant | optional suffix | `.solid.svg` |

## Asset IDs

```
AALVIZ-{KIND}-{SEMANTIC}-{NNN}
```

Examples:

- `AALVIZ-ICON-AUTH-OBSERVED-001`
- `AALVIZ-GRAPH-NODE-CANONICAL_STATE-001`
- `AALVIZ-BRAND-PRIMARY_SYMBOL`

## Kind codes

| Code | Meaning |
|------|---------|
| `BRAND` | Identity |
| `ICON-AUTH` | Authority / epistemic |
| `ICON-ACT` | Activation lane |
| `ICON-NAV` | Navigation |
| `ICON-SYS` | Subsystem |
| `GRAPH-NODE` | Node primitive |
| `GRAPH-EDGE` | Edge style sample |
| `GRAPH-PORT` | Port / junction |
| `RUNE` | Reserved batch 2 |

## Rules

1. One semantic role → one master outline SVG.
2. Badge/solid variants are derivatives, not new semantics.
3. Never encode color in the filename (`observed-blue.svg` forbidden).
4. Never put version numbers in filenames; version lives in the manifest.
5. `currentColor` only in icon masters (brand lockups may use fixed tokens).
