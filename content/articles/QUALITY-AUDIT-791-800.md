# Quality audit — HOME articles 791–800

## Result

- Canonical topic intents reviewed: **10/10**.
- Published unique intents: **10**; bilingual article JSON files: **20/20 PASS**.
- FAQ answer-to-section mappings: **60/60 PASS**.
- Schema, IDs, slugs, translation groups, locales, SEO fields, four H2 sections, three FAQs, image metadata, status, safety checks and collision checks all pass.
- Meta descriptions are complete first editorial sentences; character truncation is rejected.
- Blocking errors: **0**. Warnings: **0**.

## Validation evidence

- Final full GitHub Actions validation: run **34279628273** — PASS.
- Generation, independent validation, generated-state commit, and post-commit validation all completed successfully.
- Final validated inventory: **10 entries / 20 bilingual article JSONs / 60 FAQ mappings / 0 errors / 0 warnings**.
- Manual review covered the window pair (#793/#794), boiler reset safety (#795), dehumidifier operation/placement (#796/#797), musty-closet removal/prevention (#798/#799), and furnace-filter identification (#800).
- Manual FAQ review corrected **#795** so the repeated-lockout question now answers directly that another failure means stop resetting and request service.
- Manual FAQ review corrected **#798** so the return-to-closet question now states directly that the closet and stored items must both be completely dry.
- Manual SEO/intention review reclassified **#800** as an `identification-guide` and replaced title-shaped intent wording with natural observable-signs wording in ES and EN.

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
- #800 identifies filter loading without duplicating replacement interval (#366), MERV selection (#367), airflow direction (#368), or air-conditioning filter checks (#728).
- Spanish and English are localized independently while preserving shared intent and translation groups.
- Temporary batch, generator and workflow were removed before PR/merge.
