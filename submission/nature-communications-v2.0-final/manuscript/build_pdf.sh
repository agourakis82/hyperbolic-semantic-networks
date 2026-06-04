#!/usr/bin/env bash
# Build the review + preprint PDFs from main.md (pandoc + tectonic).
# Requires: pip install pypandoc_binary ; tectonic on PATH.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
FIGDIR="$(cd "$HERE/../figures" && pwd)"
PANDOC="$(python3 -c 'import pypandoc; print(pypandoc.get_pandoc_path())')"
mk(){ # $1=outfile  $2=extra-yaml-file
  { cat "$2"; sed -n '9,$p' "$HERE/main.md"; } > /tmp/_m.md
  python3 - "$FIGDIR" <<'PY'
import sys,os; FIG=sys.argv[1]; p="/tmp/_m.md"; s=open(p).read()
s=s.replace("**Figure 1 – Clustering–Curvature Map Across Networks.**","![Figure 1 — Clustering–Curvature Map (7-graph).](%s/figure1_clustering_curvature_7graph.png){width=85%%}\n\n**Figure 1 – Clustering–Curvature Map Across Networks.**"%FIG,1)
s=s.replace("**Figure 4 – Phase Diagram of Network Geometry.**","![Figure 4 — Phase Diagram (7-graph).](%s/figure4_phase_diagram_7graph.png){width=85%%}\n\n**Figure 4 – Phase Diagram of Network Geometry.**"%FIG,1)
open(p,"w").write(s)
PY
  shift 2
  "$PANDOC" /tmp/_m.md -o "$1" --pdf-engine=tectonic -H "$HERE/_build_header.tex" --toc --toc-depth=2 -V colorlinks=true -V linkcolor=blue "$@"
}
# review (clean manuscript)
printf '%s\n' '---' 'title: "Boundary Conditions for Hyperbolic Geometry in Semantic Networks"' 'subtitle: "Construction-Dependent Curvature Revealed by Ollivier–Ricci Analysis"' 'author: "Demetrios C. Agourakis"' 'geometry: margin=1in' 'fontsize: 11pt' '---' '' > /tmp/_yh.yaml
mk "$HERE/main_review_v2.0-final.pdf" /tmp/_yh.yaml
echo "built main_review_v2.0-final.pdf"
