# EMX025 coverage-gap audit

No new dynamics or composite law ran. The machine-readable matrix covers all 76 retained constraints across DEV167 and EMX019–024.

## Observed loci

- Linear harmonic and bending families miss the transverse/loading locus.
- Nonlinear central bonds assess transverse and loading difference, but have fixed component-only symmetry sensitivity.
- Internal orientation preserves a separate orientation response (relevant to T18) but has no matched loading difference.

## Ranked follow-ups

1. `COMBINED_NONLINEAR_CENTRAL_PLUS_INTERNAL_ORIENTATION_CONTRACT_GATE` — combines EMX022’s only assessed loaded/unloaded difference with EMX024’s transverse/internal-orientation coverage; one law can be tested against both loci
2. `LATTICE_COVARIANT_NONLINEAR_CENTRAL_SYMMETRY_CONTROL_GATE` — resolves whether EMX022 component-only y/z sensitivity is a representation-control mismatch or a genuine constraint failure
3. `INTERNAL_ORIENTATION_TO_NATIVE_T18_OBSERVABLE_BRIDGE_GATE` — resolves the still-not-assessed meaning-preserving bridge between EMX024 s,w and native T18 orientation/strain terms

Ranking is frozen by coverage value only; no winner is inferred.
