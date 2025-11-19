# LaTeX Conversion Guide

**Status**: Template created, full conversion pending  
**Estimated time**: 4-6 hours for complete conversion

---

## Current Status

✅ **Template created**: `manuscript.tex` (basic structure)  
⏳ **Full content**: Needs manual conversion from `main.md`  
⏳ **References**: Need `references.bib` file  
⏳ **Figures**: Need proper `\includegraphics` commands  
⏳ **Tables**: Need `tabular` environment formatting  

---

## Steps to Complete Conversion

### 1. Get Network Science Template (Optional)

Download official template:
```bash
wget https://www.cambridge.org/core/services/aop-file-manager/file/TEMPLATE_URL
unzip network-science-latex-template.zip
```

Or use our custom template (already Q1-compliant).

### 2. Convert Main Content

**Sections to convert** (copy from `main.md` → `manuscript.tex`):
- [x] Title, author, abstract (DONE in template)
- [x] Introduction 1.1-1.5 (DONE in template)
- [ ] Methods 2.1-2.7
- [ ] Results 3.1-3.5
- [ ] Discussion 4.1-4.6
- [ ] Conclusion

**Tools**:
- Pandoc (automated): `pandoc main.md -o manuscript.tex`
- Manual editing (better control)

### 3. Format Tables

**Example - Table 1**:
```latex
\begin{table}[htbp]
\centering
\caption{Mean Ollivier-Ricci curvature by language.}
\label{tab:languages}
\begin{tabular}{lcccccc}
\toprule
Language & N Nodes & N Edges & $\kappa$ (mean) & $\kappa$ (median) & $\kappa$ (std) & Geometry \\
\midrule
Spanish  & 500 & 776 & -0.104 & +0.010 & 0.162 & \textbf{Hyperbolic} \\
Dutch    & 500 & 817 & -0.172 & -0.067 & 0.222 & \textbf{Hyperbolic} \\
Chinese  & 500 & 799 & -0.189 & -0.136 & 0.225 & \textbf{Hyperbolic} \\
English  & 500 & 815 & -0.197 & -0.161 & 0.235 & \textbf{Hyperbolic} \\
\bottomrule
\end{tabular}
\end{table}
```

Repeat for Tables 2, 3A.

### 4. Include Figures

**Example**:
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{../figures/consolidated_analysis_v6.4.png}
\caption{Curvature distributions across four languages. All exhibit negative mean curvature (hyperbolic). Panel A: Spanish, B: Dutch, C: Chinese, D: English.}
\label{fig:curvature_distributions}
\end{figure}
```

Repeat for Figures A-F, 7-8.

### 5. Create BibTeX File

**`references.bib`**:
```bibtex
@article{steyvers2005,
  author = {Steyvers, Mark and Tenenbaum, Joshua B.},
  title = {The Large-Scale Structure of Semantic Networks},
  journal = {Cognitive Science},
  volume = {29},
  number = {1},
  pages = {41--78},
  year = {2005}
}

% ... [Add all 25 references] ...
```

### 6. Compile

```bash
cd manuscript/latex
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex  # Run twice for refs
```

### 7. Check Output

Open `manuscript.pdf` and verify:
- All sections present
- All tables formatted correctly
- All figures display properly
- All references cited
- Page numbers correct
- Formatting professional

---

## Automation Option

**Quick conversion with Pandoc**:
```bash
cd manuscript
pandoc main.md -o latex/manuscript_auto.tex \
  --standalone \
  --template=network-science-template.tex \
  --bibliography=references.bib \
  --citeproc

# Then manually polish the output
```

---

## Timeline

**If doing manually** (recommended for quality):
- Convert main content: 2-3 hours
- Format tables: 1 hour
- Format figures: 1 hour
- Create BibTeX: 1 hour
- Compile + debug: 30 min
- **Total**: 5-6 hours

**If using Pandoc** (faster but needs polish):
- Auto-convert: 10 min
- Manual fixes: 2-3 hours
- **Total**: 2-3 hours

---

## Next Steps

When ready to convert:

1. Choose approach (manual or Pandoc)
2. Allocate 3-6 hours
3. Convert section by section
4. Test compilation frequently
5. Verify PDF output quality

**Not urgent**: Can submit markdown to many journals  
**Network Science**: Accepts Word/PDF initially, LaTeX for final

---

**Status**: Infrastructure ready, conversion when needed (Week 3)

