# Historical census protocol

The build tool hashes and imports the canonical mechanism registry, development
ledger, and historical attempt index. It also searches canonical tracked paths
and reachable commits for the required historical DEV ranges and representation
terms. Canonical code and deterministic numeric artifacts outrank prose if they
conflict. An unresolved conflict is marked `AMBIGUOUS`, never silently repaired.

The local canonical checkout is intentionally not fetched, checked out, or
written. The snapshot records its exact branch, commit, hashes, and timestamp.
