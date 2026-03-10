#!/usr/bin/env python3
"""
acquire_networks.py — Download and preprocess additional semantic network datasets.

Produces CSV files in data/processed/ with format: source,target,weight
(for association networks) or source,target,weight,relation (for knowledge graphs).

Datasets acquired automatically (no account/registration required):
  eat_en      — Edinburgh Associative Thesaurus (GitHub)
  framenet_en — FrameNet 1.7 frame relations (NLTK)
  conceptnet_it / de / fr / ja / ar_full — ConceptNet API (no auth)

Datasets requiring manual download (instructions printed):
  swow_rp     — SWOW Rioplatense Spanish (smallworldofwords.org/project/research)
  swow_fr/de/it/ja — SWOW additional languages (same portal)
  usf_en      — USF Free Association (w3.usf.edu/FreeAssociation/)

Usage:
  python3 julia/scripts/acquire_networks.py             # all auto datasets
  python3 julia/scripts/acquire_networks.py eat_en      # single dataset
  python3 julia/scripts/acquire_networks.py --list      # list all targets
  python3 julia/scripts/acquire_networks.py --manual    # print manual instructions
"""

import sys
import os
import json
import csv
import urllib.request
import urllib.error
import urllib.parse
import zipfile
import io
import subprocess
import shutil
import collections
import time
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data" / "processed"
SCRATCH_DIR = REPO_ROOT / "data" / "scratch"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

TOP_N = 500          # top-N nodes by degree (matching existing SWOW preprocessing)
MIN_WEIGHT = 0.01    # minimum association strength to include


# ─────────────────────────────────────────────────────────────────
# Shared utilities
# ─────────────────────────────────────────────────────────────────

def save_edges(edges, out_path, with_relation=False):
    """Save list of (source, target, weight[, relation]) to CSV."""
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if with_relation:
            writer.writerow(["source", "target", "weight", "relation"])
            for row in edges:
                src, tgt, w = row[0], row[1], row[2]
                rel = row[3] if len(row) > 3 else "associated"
                writer.writerow([src, tgt, f"{float(w):.6f}", rel])
        else:
            writer.writerow(["source", "target", "weight"])
            for row in edges:
                src, tgt, w = row[0], row[1], row[2]
                writer.writerow([src, tgt, f"{float(w):.6f}"])
    n = len(edges)
    print(f"  Saved {n} edges → {Path(out_path).name}")
    return n


def select_top_nodes(edges, top_n=TOP_N):
    """Select top_n nodes by total degree, return induced subgraph."""
    degree = collections.Counter()
    for row in edges:
        u, v = row[0], row[1]
        degree[u] += 1
        degree[v] += 1
    top_nodes = set(n for n, _ in degree.most_common(top_n))
    return [row for row in edges if row[0] in top_nodes and row[1] in top_nodes]


def directed_to_undirected(edges, with_relation=False):
    """Convert directed weighted edge list to undirected (keep max weight per pair)."""
    weight = {}
    relation = {}
    for row in edges:
        u, v, w = row[0], row[1], float(row[2])
        rel = row[3] if len(row) > 3 else "associated"
        pair = (min(u, v), max(u, v))
        if w > weight.get(pair, -1):
            weight[pair] = w
            relation[pair] = rel
    if with_relation:
        return [(u, v, w, relation[(u, v)]) for (u, v), w in weight.items()]
    return [(u, v, w) for (u, v), w in weight.items()]


def http_get(url, headers=None, timeout=30):
    """HTTP GET returning bytes."""
    h = {"User-Agent": "Mozilla/5.0 (research; semantic-network-study)"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def git_clone(url, dest_dir, sparse_paths=None):
    """Shallow git clone, optionally sparse."""
    dest = Path(dest_dir)
    if dest.exists():
        print(f"  Repo already at {dest.name}/")
        return dest
    print(f"  Cloning {url.split('/')[-1]}...")
    cmd = ["git", "clone", "--depth=1"]
    if sparse_paths:
        cmd += ["--filter=blob:none", "--sparse"]
    cmd += [url, str(dest)]
    subprocess.run(cmd, check=True, capture_output=True)
    if sparse_paths:
        subprocess.run(["git", "sparse-checkout", "set"] + sparse_paths,
                       cwd=str(dest), check=True, capture_output=True)
    return dest


# ─────────────────────────────────────────────────────────────────
# EAT — Edinburgh Associative Thesaurus
# ─────────────────────────────────────────────────────────────────

def acquire_eat():
    """
    EAT (dariusk/ea-thesaurus on GitHub).
    JSON format: { "STIMULUS": [{"RESPONSE": count_str}, ...], ... }
    Stimulus words are uppercase strings (many are words, some are numbers/symbols).
    """
    out = DATA_DIR / "eat_en_edges.csv"
    if out.exists():
        print(f"  {out.name} already exists.")
        return

    repo = git_clone("https://github.com/dariusk/ea-thesaurus.git",
                     SCRATCH_DIR / "ea-thesaurus")

    # Find the JSON file
    json_files = list(repo.glob("*.json"))
    if not json_files:
        print("  ERROR: No JSON file found in ea-thesaurus repo.")
        return
    json_file = json_files[0]
    print(f"  Parsing {json_file.name} ({json_file.stat().st_size // 1024} KB)...")

    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    # Structure: { "WORD": [{"RESPONSE1": "count1"}, {"RESPONSE2": "count2"}, ...] }
    # Keys are the stimulus words (uppercase); values are lists of response dicts
    edges = []
    skipped = 0
    for stimulus, responses in data.items():
        stim = stimulus.strip().lower()
        if not stim or not stim.replace("-", "").replace("'", "").isalpha():
            skipped += 1
            continue  # skip numbers and symbols as stimuli

        if not isinstance(responses, list):
            continue

        total = sum(int(list(r.values())[0]) for r in responses if r)
        if total == 0:
            continue

        for resp_dict in responses:
            if not resp_dict:
                continue
            resp_word = list(resp_dict.keys())[0].strip().lower()
            count = int(list(resp_dict.values())[0])
            if (resp_word and resp_word != stim
                    and resp_word.replace("-", "").replace("'", "").isalpha()):
                w = count / total
                if w >= MIN_WEIGHT:
                    edges.append((stim, resp_word, w))

    print(f"  Parsed {len(edges)} directed edges from {len(data)} stimuli "
          f"(skipped {skipped} non-word stimuli)")

    edges = directed_to_undirected(edges)
    edges = select_top_nodes(edges, TOP_N)
    save_edges(edges, out)


# ─────────────────────────────────────────────────────────────────
# ConceptNet API — multiple languages
# ─────────────────────────────────────────────────────────────────

CONCEPTNET_API = "https://api.conceptnet.io"

def fetch_conceptnet_language(lang_code, max_nodes=600, max_requests=80):
    """
    Fetch ConceptNet edges for a language via the public API.
    Uses paginated /c/{lang}/ endpoint.
    Returns list of (source, target, weight, relation) tuples.
    """
    print(f"  Fetching ConceptNet-{lang_code.upper()} via API...")
    edges = []
    nodes_seen = set()
    offset = 0
    limit = 1000

    url = f"{CONCEPTNET_API}/c/{lang_code}/?limit={limit}&offset={offset}"
    requests_made = 0

    while requests_made < max_requests:
        try:
            data_bytes = http_get(url, timeout=30)
            data = json.loads(data_bytes)
        except Exception as e:
            print(f"    API error at offset {offset}: {e}")
            break

        edges_batch = data.get("edges", [])
        if not edges_batch:
            break

        for edge in edges_batch:
            start = edge.get("start", {})
            end = edge.get("end", {})
            rel = edge.get("rel", {}).get("label", "related")
            weight = float(edge.get("weight", 1.0))

            # Only keep edges where both nodes are in our target language
            if (start.get("language") != lang_code
                    or end.get("language") != lang_code):
                continue

            src_label = start.get("label", "").lower().strip()
            tgt_label = end.get("label", "").lower().strip()

            # Skip multi-word or very long labels
            if (not src_label or not tgt_label
                    or " " in src_label or " " in tgt_label
                    or len(src_label) > 20 or len(tgt_label) > 20):
                continue

            if src_label != tgt_label and weight >= 1.0:
                edges.append((src_label, tgt_label, weight, rel))
                nodes_seen.add(src_label)
                nodes_seen.add(tgt_label)

        print(f"    offset={offset}: got {len(edges_batch)} edges, "
              f"{len(nodes_seen)} unique nodes so far")

        if len(nodes_seen) >= max_nodes:
            print(f"    Reached {max_nodes} nodes, stopping.")
            break

        # Paginate via view URL or increment offset
        view = data.get("view", {})
        next_url = view.get("nextPage", "")
        if next_url:
            url = CONCEPTNET_API + next_url
        else:
            offset += limit
            url = f"{CONCEPTNET_API}/c/{lang_code}/?limit={limit}&offset={offset}"

        requests_made += 1
        time.sleep(0.3)  # polite rate limiting

    print(f"  Fetched {len(edges)} directed edges, {len(nodes_seen)} nodes")
    return edges


def acquire_conceptnet_lang(lang_code, lang_name):
    """Acquire ConceptNet for a language via API."""
    out = DATA_DIR / f"conceptnet_{lang_code}_edges.csv"
    if out.exists() and sum(1 for _ in open(out)) > 10:
        print(f"  {out.name} already exists (adequate size).")
        return

    edges = fetch_conceptnet_language(lang_code, max_nodes=600)
    if not edges:
        print(f"  No edges fetched for ConceptNet-{lang_code}.")
        return

    edges = directed_to_undirected(edges, with_relation=True)
    edges = select_top_nodes(edges, TOP_N)
    n = save_edges(edges, out, with_relation=True)
    if n < 50:
        print(f"  WARNING: only {n} edges — ConceptNet-{lang_code} may be too sparse.")


# ─────────────────────────────────────────────────────────────────
# FrameNet — semantic frames
# ─────────────────────────────────────────────────────────────────

def acquire_framenet():
    """
    FrameNet 1.7 frame-to-frame relations via NLTK.
    Nodes = frames; edges = frame relations weighted by type.
    Expected: sparse taxonomy-like graph → Euclidean (low C, low η).
    """
    out = DATA_DIR / "framenet_en_edges.csv"
    if out.exists():
        print(f"  {out.name} already exists.")
        return

    # Ensure NLTK is available
    try:
        import nltk
    except ImportError:
        print("  Installing nltk...")
        subprocess.run([sys.executable, "-m", "pip", "install", "nltk", "-q"], check=True)
        import nltk

    nltk.download("framenet_v17", quiet=True)

    try:
        from nltk.corpus import framenet as fn
    except LookupError:
        print("  FrameNet data not available. Attempting download...")
        nltk.download("framenet_v17")
        from nltk.corpus import framenet as fn

    frames = list(fn.frames())
    print(f"  FrameNet loaded: {len(frames)} frames")

    # Relation type weights
    rel_weight = {
        "Inheritance": 1.0,
        "Causative_of": 0.9,
        "Inchoative_of": 0.9,
        "Using": 0.7,
        "Subframe": 0.8,
        "Precedes": 0.7,
        "Perspective_on": 0.6,
        "ReFraming_Mapping": 0.5,
    }

    edges_dict = {}
    for frame in frames:
        fname = frame.name.lower().replace("_", " ")
        for rel in frame.frameRelations:
            sup = rel.superFrameName.lower().replace("_", " ")
            sub = rel.subFrameName.lower().replace("_", " ")
            rel_type = rel.type.name
            w = rel_weight.get(rel_type, 0.4)
            pair = (min(sup, sub), max(sup, sub))
            if edges_dict.get(pair, 0) < w:
                edges_dict[pair] = w

    edges = [(u, v, w) for (u, v), w in edges_dict.items() if u != v]
    print(f"  FrameNet: {len(edges)} undirected frame-relation edges")

    # FrameNet has ~1,200 frames — keep all (within our N range)
    save_edges(edges, out)


# ─────────────────────────────────────────────────────────────────
# USF Free Association Norms
# ─────────────────────────────────────────────────────────────────

def acquire_usf():
    """
    USF Free Association Norms.
    Tries Pajek mirror at vlado.fmf.uni-lj.si.
    Falls back to instructions for manual download.
    """
    out = DATA_DIR / "usf_en_edges.csv"
    if out.exists():
        print(f"  {out.name} already exists.")
        return

    # Check for manually placed scratch file first
    manual = SCRATCH_DIR / "usf_raw.txt"
    if manual.exists():
        print(f"  Found manual USF file at scratch/usf_raw.txt")
        edges = _parse_usf_text(manual.read_text(encoding="latin-1"))
        if edges:
            edges = directed_to_undirected(edges)
            edges = select_top_nodes(edges, TOP_N)
            save_edges(edges, out)
            return

    # Try Pajek mirror
    pajek_url = "http://vlado.fmf.uni-lj.si/pub/networks/data/dic/fa/FreeAssoc.zip"
    try:
        print("  Trying Pajek mirror for USF...")
        data = http_get(pajek_url, timeout=60)
        zf = zipfile.ZipFile(io.BytesIO(data))
        net_files = [n for n in zf.namelist()
                     if n.lower().endswith(".net") or n.lower().endswith(".paj")]
        if net_files:
            content = zf.read(net_files[0]).decode("latin-1")
            edges = _parse_pajek_net(content)
            if edges:
                edges = select_top_nodes(edges, TOP_N)
                save_edges(edges, out)
                return
    except Exception as e:
        print(f"  Pajek mirror failed: {e}")

    print("  MANUAL REQUIRED: USF Free Association Norms")
    print("  1. Download from http://w3.usf.edu/FreeAssociation/")
    print("  2. Place tab-delimited file as:")
    print(f"     {SCRATCH_DIR / 'usf_raw.txt'}")
    print("  3. Rerun: python3 acquire_networks.py usf_en")


def _parse_pajek_net(content):
    vertices = {}
    edges = []
    mode = None
    for line in content.splitlines():
        line = line.strip()
        low = line.lower()
        if low.startswith("*vertices"):
            mode = "v"; continue
        if low.startswith("*arcs") or low.startswith("*edges"):
            mode = "e"; continue
        if line.startswith("*"):
            mode = None; continue
        if mode == "v" and line:
            parts = line.split(None, 2)
            if len(parts) >= 2:
                idx = int(parts[0])
                name = parts[1].strip('"\'').lower()
                vertices[idx] = name
        elif mode == "e" and line:
            parts = line.split()
            if len(parts) >= 3:
                u, v, w = int(parts[0]), int(parts[1]), float(parts[2])
                if u in vertices and v in vertices:
                    edges.append((vertices[u], vertices[v], w))
    return edges


def _parse_usf_text(content):
    """Parse USF tab-delimited format: CUE\tTARGET\t...\tFSG\t..."""
    edges = []
    for line in content.splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 6:
            try:
                cue = parts[0].strip().lower()
                target = parts[1].strip().lower()
                fsg = float(parts[5])
                if cue and target and cue != target and fsg >= MIN_WEIGHT:
                    edges.append((cue, target, fsg))
            except (ValueError, IndexError):
                pass
    return edges


# ─────────────────────────────────────────────────────────────────
# SWOW additional languages — manual download instructions
# ─────────────────────────────────────────────────────────────────

def swow_manual_instructions(lang_code, lang_name):
    """Print instructions for manual SWOW download."""
    out = DATA_DIR / f"swow_{lang_code}_edges.csv"
    if out.exists():
        print(f"  {out.name} already exists.")
        return

    # Check if manually placed scratch file exists
    scratch = SCRATCH_DIR / f"swow_{lang_code}_raw.csv"
    if scratch.exists():
        print(f"  Found manual file: {scratch.name}")
        _process_swow_manual(scratch, out)
        return

    print(f"  MANUAL REQUIRED: SWOW-{lang_name.upper()}")
    print(f"  1. Go to https://smallworldofwords.org/project/research/")
    print(f"  2. Request/download the {lang_name} dataset (balanced R70 format)")
    print(f"  3. Place the CSV as: {scratch}")
    print(f"     Expected columns: cue, R1[, R2, R3] or cue, response")
    print(f"  4. Rerun: python3 acquire_networks.py swow_{lang_code}")


def _process_swow_manual(csv_path, out_path):
    """Process a manually downloaded SWOW CSV (cue + R1[,R2,R3] format)."""
    pairs = collections.Counter()
    cue_totals = collections.Counter()

    with open(csv_path, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = [c.lower().strip() for c in (reader.fieldnames or [])]

        # Detect response columns
        resp_cols = []
        cue_col = None
        for fn in fieldnames:
            if fn in ("cue", "cueword", "stimulus"):
                cue_col = fn
            elif fn in ("r1", "r2", "r3", "response", "response1", "response2", "response3"):
                resp_cols.append(fn)

        if not cue_col or not resp_cols:
            print(f"  WARNING: Could not detect cue/response columns in {csv_path.name}")
            print(f"  Columns found: {fieldnames}")
            return

        print(f"  Parsing {csv_path.name}: cue={cue_col}, responses={resp_cols}")
        for row in reader:
            row_lower = {k.lower().strip(): v for k, v in row.items()}
            cue = row_lower.get(cue_col, "").strip().lower()
            if not cue:
                continue
            for rc in resp_cols:
                resp = row_lower.get(rc, "").strip().lower()
                if resp and resp != cue and resp not in ("x", "na", "n/a", "none", ""):
                    pairs[(cue, resp)] += 1
                    cue_totals[cue] += 1

    edges = []
    for (cue, resp), count in pairs.items():
        w = count / max(cue_totals[cue], 1)
        if w >= MIN_WEIGHT:
            edges.append((cue, resp, w))

    edges = directed_to_undirected(edges)
    edges = select_top_nodes(edges, TOP_N)
    n = save_edges(edges, out_path)
    print(f"  Processed {n} edges from SWOW manual file.")


# ─────────────────────────────────────────────────────────────────
# Dataset registry
# ─────────────────────────────────────────────────────────────────

AUTO_DATASETS = {
    "eat_en": {
        "desc": "Edinburgh Associative Thesaurus — British English (GitHub)",
        "fn": acquire_eat,
    },
    "framenet_en": {
        "desc": "FrameNet 1.7 frame relations (NLTK, no download required)",
        "fn": acquire_framenet,
    },
    "conceptnet_it": {
        "desc": "ConceptNet Italian (API, no auth)",
        "fn": lambda: acquire_conceptnet_lang("it", "Italian"),
    },
    "conceptnet_de": {
        "desc": "ConceptNet German (API, no auth)",
        "fn": lambda: acquire_conceptnet_lang("de", "German"),
    },
    "conceptnet_fr": {
        "desc": "ConceptNet French (API, no auth)",
        "fn": lambda: acquire_conceptnet_lang("fr", "French"),
    },
    "conceptnet_ja": {
        "desc": "ConceptNet Japanese (API, no auth)",
        "fn": lambda: acquire_conceptnet_lang("ja", "Japanese"),
    },
    "usf_en": {
        "desc": "USF Free Association Norms (tries auto; falls back to manual)",
        "fn": acquire_usf,
    },
}

MANUAL_DATASETS = {
    "swow_rp": {
        "desc": "SWOW Rioplatense Spanish",
        "fn": lambda: swow_manual_instructions("rp", "Rioplatense Spanish"),
    },
    "swow_fr": {
        "desc": "SWOW French",
        "fn": lambda: swow_manual_instructions("fr", "French"),
    },
    "swow_de": {
        "desc": "SWOW German",
        "fn": lambda: swow_manual_instructions("de", "German"),
    },
    "swow_it": {
        "desc": "SWOW Italian",
        "fn": lambda: swow_manual_instructions("it", "Italian"),
    },
    "swow_ja": {
        "desc": "SWOW Japanese",
        "fn": lambda: swow_manual_instructions("ja", "Japanese"),
    },
}

ALL_DATASETS = {**AUTO_DATASETS, **MANUAL_DATASETS}


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--list" in args:
        print("Automatically acquirable datasets:")
        for k, v in AUTO_DATASETS.items():
            exists = "✓" if (DATA_DIR / f"{k}_edges.csv").exists() else " "
            print(f"  [{exists}] {k:20s}  {v['desc']}")
        print("\nManual download required:")
        for k, v in MANUAL_DATASETS.items():
            exists = "✓" if (DATA_DIR / f"{k}_edges.csv").exists() else " "
            print(f"  [{exists}] {k:20s}  {v['desc']}")
        return

    if "--manual" in args:
        print("\nManual download instructions:")
        for k, v in MANUAL_DATASETS.items():
            print(f"\n{'─'*50}")
            v["fn"]()
        return

    targets = [a for a in args if not a.startswith("-")]
    if not targets:
        targets = list(AUTO_DATASETS.keys())  # default: auto only

    results = {}
    for name in targets:
        if name not in ALL_DATASETS:
            print(f"Unknown dataset: {name}. Run --list to see options.")
            continue
        print(f"\n{'='*60}")
        print(f"Acquiring: {name}")
        print(f"  {ALL_DATASETS[name]['desc']}")
        print(f"{'='*60}")
        try:
            ALL_DATASETS[name]["fn"]()
            out = DATA_DIR / f"{name}_edges.csv"
            if out.exists():
                n_edges = sum(1 for _ in open(out)) - 1  # subtract header
                if n_edges >= 50:
                    results[name] = f"OK ({n_edges} edges)"
                else:
                    results[name] = f"WARNING: only {n_edges} edges (too sparse?)"
            else:
                results[name] = "SKIPPED (manual download needed)"
        except Exception as e:
            results[name] = f"FAILED: {e}"
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("Summary:")
    for name, status in results.items():
        print(f"  {name:25s}  {status}")
    print(f"\nOutput directory: {DATA_DIR}")
    print("\nNext steps:")
    print("  1. Add acquired networks to julia/scripts/unified_semantic_orc.jl")
    print("  2. Run: julia --project=julia julia/scripts/unified_semantic_orc.jl")


if __name__ == "__main__":
    main()
