# Quality audit 071–150 — final validation

This report is generated from the branch contents after the editorial pass. Word counts refer to visible words in `content_html`; they are diagnostic, not length targets.

## Validation

- JSON files checked: **160** (80 ES + 80 EN expected)
- Structural/editorial validation: **PASS**
- Targeted final corrections applied in this pass: **18** field-level changes

## Quantitative profile

| Range | ES words | ES H2 | ES FAQ | ES sources | EN words | EN H2 | EN FAQ | EN sources |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 071-100 | 785.4 | 9.3 | 4.0 | 1.6 | 704.6 | 9.5 | 4.0 | 1.6 |
| 101-114 | 585.2 | 7.6 | 3.7 | 1.3 | 541.1 | 7.6 | 3.7 | 1.2 |
| 115-120 | 595.2 | 10.2 | 3.0 | 1.2 | 549.5 | 10.2 | 3.0 | 1.2 |
| 121-130 | 408.9 | 6.7 | 3.0 | 1.3 | 383.0 | 6.7 | 3.0 | 1.3 |
| 131-150 | 376.1 | 6.9 | 3.0 | 1.8 | 353.2 | 6.9 | 3.0 | 1.8 |

The lower averages in later blocks were reviewed editorially rather than treated as automatic failures. Compact articles were retained when they fully resolve the intent; troubleshooting and safety topics were checked for decision branches, distinguishing signals, stop conditions, and escalation points.

## Intent-overlap watchlist

Sequence similarity and vocabulary Jaccard are diagnostics only. Each listed pair was also read for intent separation.

| Lang | Pair | Sequence similarity | Vocabulary Jaccard |
|---|---|---:|---:|
| ES | #72 / #73 | 0.296 | 0.271 |
| EN | #72 / #73 | 0.338 | 0.346 |
| ES | #132 / #133 | 0.269 | 0.202 |
| EN | #132 / #133 | 0.256 | 0.239 |
| ES | #135 / #136 | 0.136 | 0.220 |
| EN | #135 / #136 | 0.169 | 0.216 |
| ES | #140 / #141 | 0.245 | 0.248 |
| EN | #140 / #141 | 0.287 | 0.300 |
| ES | #144 / #145 | 0.178 | 0.149 |
| EN | #144 / #145 | 0.196 | 0.173 |
| ES | #148 / #150 | 0.198 | 0.258 |
| EN | #148 / #150 | 0.245 | 0.273 |
| ES | #149 / #150 | 0.268 | 0.191 |
| EN | #149 / #150 | 0.268 | 0.208 |

Editorial review confirmed distinct intents for oil vs food grease (#72/#73), cause vs reduction of humidity (#132/#133), cause vs prevention of window condensation (#135/#136), household fabrics vs clothing (#140/#141), storage duration vs spoilage checks for eggs (#144/#145), and microwave compatibility/no-heat/sparking diagnostics (#148/#149/#150).

## Final editorial notes

- #103 and #105–108 retain their existing depth: the troubleshooting/energy intent is already resolved without padding.
- #121–130 were reviewed individually; concise procedures were not expanded where they already passed the second-search test.
- #131–150 were reviewed individually in both languages. Safety-critical appliance topics state what is safe, what to check, when to stop using the appliance, and what the user should not open or repair.
- EN source-note metadata in #111–120 was localized to English; truncated SEO titles were completed; Spanish climatization wording was normalized where required.
- `status: publish`, article numbers, translation groups, slugs, and JSON structure were preserved.
