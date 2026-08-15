# EMX043 — Unrecoverable-provenance replay note

## Status

These 31 cells are **not failures**. They have prior result summaries, but no
saved, hash-pinned full native state history sufficient to apply the EMX041
shared observer and EMX042 universal-admission gates.

They must remain classified as `UNRECOVERABLE_PROVENANCE` until an archival
replay is possible. They must not be counted as rejected candidates.

## Why the summaries are insufficient

The shared observer requires a complete time-resolved native state with all of
the following fixed and verifiable:

- initial/source state;
- lattice and geometry;
- boundary condition;
- timestep and duration;
- source/preparation history;
- observer inputs and analysis window.

The retained aggregate outputs do not uniquely determine those inputs.
Reconstructing a run from the summaries would introduce a new state,
preparation, or dynamics choice, so it would not be a valid replay.

## Cells retained for future archival replay

1. `B01_TWO_SPECIES_UNIT_CELL`
2. `B02_MULTI_SITE_UNIT_CELL`
3. `C01_BILAYER_SUBSTRATE_UPPER`
4. `C02_MULTILAYER`
5. `D01_RECIPROCAL_ORIENTATION_TRANSLATION`
6. `D02_DISCRETE_INTERNAL_STATE`
7. `E01_NONCENTRAL_MULTIBODY`
8. `E02_FINITE_RANGE`
9. `F01_PERIODIC_LOOP_OBSERVER`
10. `F02_DEFECT_BOUNDARY_PROTOCOL`
11. `G01_EXPLICIT_STABLE_CAUSAL_UPDATE`
12. `EMX020`
13. `EMX022`
14. `EMX023`
15. `EMX024`
16. `EMX026`
17. `EMX028`
18. `EMX030:A01`
19. `EMX030:F01`
20. `EMX031:D01`
21. `EMX031:E01`
22. `EMX033:B01_PLUS`
23. `EMX033:B01_MINUS`
24. `EMX033:C01_PLUS`
25. `EMX033:C01_MINUS`
26. `EMX033:B02_BASE`
27. `EMX033:C02_BASE`
28. `EMX034:D02_BASE`
29. `EMX034:E02_BASE`
30. `EMX034:F02_BASE`
31. `EMX034:G01_BASE`

## Requirements before reassessment

For any future replay, first freeze a contract that names the exact source
artifact or deterministic replay rule, hashes every required input, and saves
the full native history and shared-observer inputs. Then evaluate the replay
under the unchanged universal-admission gates. A result may be classified only
as `UNIVERSAL_VIABLE_NONUNIQUE`, `UNIVERSAL_REJECTED`, or remain
`UNRECOVERABLE_PROVENANCE` with the missing item recorded.

## Related evidence

- `runs/emx043/universal_unassessed_completion_matrix.json`
- `runs/emx043/repository_and_canonical_search_results.json`
- `runs/emx041/shared_observer_definition.json`
