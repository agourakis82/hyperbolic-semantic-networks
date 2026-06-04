# Citation audit — `[N]` ↔ references (v2.0-final)

**Status: the in-text `[N]` numbering cannot be auto-aligned to the bibliography**, because the bibliography is incomplete (~half the cited `[N]` have no entry) and the numbering does not match bib order (e.g. `[9]` = Ollivier 2009, which is the 7th `.bib` entry). Completing it requires the author to supply the **missing references** — these cannot be reconstructed without inventing real papers, which we will not do.

Below is the exact punch-list. Once the **MISSING** rows are filled, converting `[N]` → `[@key]` + a numeric CSL is a single mechanical pass (see `build_pdf.sh`).

| `[N]` | In-text context | Status | Key / action |
|---|---|---|---|
| `[1-3]` | small-world structure, modularity, degree heterogeneity | LIKELY | candidates: `newman2003`, `steyvers2005`, `siew2019` — confirm the 3 + order |
| `[4-7]` | hyperbolic, hierarchical/branching structure of associations | **MISSING** | needs hyperbolic-network refs (e.g. Krioukov et al. 2010; foundational hyperbolic-geometry-of-networks) |
| `[7,8]` | layered lexical architecture / semantic memory | PARTIAL | `[7]` reused; `[8]` missing |
| `[9]` | "Ollivier–Ricci curvature [9]" | ✅ CONFIRMED | `ollivier2009` |
| `[13]` | "GraphRicciCurvature Python library [13]" | ✅ ADDED | `graphriccicurvature` |
| `[14]` | "powerlaw Python library [14]" | ✅ ADDED | `alstott2014` (and `clauset2009` for the CSN protocol named in §3.2.1) |
| `[16]` | "discrete Ricci flow [16]" (Following Ni et al. 2019) | ✅ CONFIRMED | `ni2019` |
| `[19-23]` | molecular interaction / brain connectomics / knowledge-graph applications | LIKELY-PARTIAL | `ni2015`, `sandhu2015`, `elumalai2022`, `simhal2020` (+1 missing) |
| `[21]` | "recent re-analyses of semantic network topology" (broad-scale) | **MISSING** | needs the broad-scale-not-scale-free ref (e.g. Broido & Clauset 2019) |
| `[24-27]` | schizophrenia-spectrum speech | LIKELY-PARTIAL | `nettekoven2023`, `mota2012`, `kapur2003` (+1) |
| `[28,29]` | depression / mania speech | AMBIGUOUS | `heladepdet2023`? + 1 — confirm |
| `[30,31]` | neurodegeneration / autism | **MISSING** | needs Alzheimer/ASD language-network refs |
| `[33]` | "hyperbolic embeddings capture hierarchy" | **MISSING** | likely Nickel & Kiela 2017 (Poincaré embeddings) |
| `[34]` | "enable efficient routing" | **MISSING** | likely Boguñá/Krioukov greedy-routing |
| `[35-37]` | "enhance machine-learning performance" | PARTIAL | `tifrea2019`, `liwuevans2020` (+1 missing) |

## Bib entries present but not clearly cited by any `[N]`
`cohen1988, efron1994, borenstein2009, higgins2003, mann1947, heaps1978, zipf1949, mcnamara2005, landauer1997, chung1997, vonluxburg2007, mowshowitz2012, faul2007, cumming2014, church1990, salton1988` — these are stats/methods references; verify whether they are cited in Methods §2.x or are leftovers from an earlier draft, and assign or remove.

## To finish (author action)
1. Fill the **MISSING** rows above with the real references (your original numbered list, if it exists, resolves all of this at once).
2. Complete `heladepdet2023` (still shows "[TO COMPLETE]" in `.bib`).
3. Then run a one-pass `[N]` → `[@key]` conversion and build with a numeric CSL (`--citeproc --csl=<numeric>.csl`) for a fully-linked, submittable bibliography.
