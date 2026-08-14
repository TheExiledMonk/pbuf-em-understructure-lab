# PBUF EM Understructure Lab

EMX001 is a separate, non-destructive historical representation census for the
PBUF electromagnetic-understructure question. It preserves defensible native
representations and compatible regimes as a frozen matrix; it does not claim
an EM mapping, alter the DEV167 law, run the matrix, or change the canonical
repository.

The canonical evidence source is `TheExiledMonk/lab`, read-only. Build the
frozen artifacts from the locally frozen checkout with:

```bash
python3 tools/build_emx001_candidate_census.py --canonical /home/fabian/lab-main-consolidation
python3 tools/validate_emx_matrix.py
python3 -m unittest discover -s tests -v
```

See [EMX001.md](docs/EMX001.md) for the development contract and
[EMX_HISTORICAL_CENSUS.md](docs/EMX_HISTORICAL_CENSUS.md) for import method.
