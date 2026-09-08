# Quality audit — HOME articles 791–800

## Result

- Canonical topic intents reviewed: **10/10**.
- Published unique intents: **10**; bilingual article JSON files: **20/20 PASS**.
- FAQ answer-to-section mappings: **60/60 PASS**.
- Schema, IDs, slugs, translation groups, locales, SEO fields, four H2 sections, three FAQs, image metadata, status, safety checks and collision checks all pass.
- Meta descriptions are complete first editorial sentences; character truncation is rejected.

## Depth metrics

- Spanish body words: min **159**, median **184**, max **205**.
- English body words: min **155**, median **182**, max **201**.
- The 150-word floor is only an incomplete-output regression guard, not an editorial target.

## Cannibalization diagnostics

- #791 vs #721: **0.149** maximum ES/EN token Jaccard.
- #792 vs #710: **0.196** maximum ES/EN token Jaccard.
- #793 vs #794: **0.127** maximum ES/EN token Jaccard.
- #795 vs #723: **0.149** maximum ES/EN token Jaccard.
- #795 vs #724: **0.196** maximum ES/EN token Jaccard.
- #796 vs #797: **0.137** maximum ES/EN token Jaccard.
- #798 vs #799: **0.168** maximum ES/EN token Jaccard.
- #800 vs #728: **0.209** maximum ES/EN token Jaccard.
- #800 vs #366: **0.224** maximum ES/EN token Jaccard.
- #800 vs #367: **0.116** maximum ES/EN token Jaccard.
- #800 vs #368: **0.127** maximum ES/EN token Jaccard.

## Sources

- Topic pairs with a directly relevant structured reference: **8**.
- Topic pairs intentionally without a structured source because no directly supporting source was mapped: **2**.

## Editorial safeguards

- #793 and #794 are separated as whole-window closure vs latch engagement.
- #795 permits only manufacturer-approved user reset steps; repeated lockout, gas odor, major leak or overheating require escalation.
- #796 and #797 separate how to operate a dehumidifier from where to place it, with wet-location and drainage limits.
- #798 removes an existing musty closet odor; #799 prevents recurrence.
- #800 diagnoses filter loading without duplicating replacement interval (#366), MERV selection (#367), airflow direction (#368), or air-conditioning filter checks (#728).
- Temporary source batch, generator and workflow must be removed before merge to `main`.
