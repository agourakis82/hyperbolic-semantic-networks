"""
Extract WordNet (oewn:2024) synsets as hyperedges for ORCHID ORC analysis.

Two types of hyperedges:
1. Synset membership: each synset is a hyperedge over its member lemmas
2. Hypernymy: each (child_synset, parent_synset) pair yields a hyperedge
   containing all lemmas of both synsets

Output: data/processed/wordnet_en_hyperedges.json
"""
import json
import wn
from collections import defaultdict

LEXICON = "oewn:2024"
TOP_N = 500  # limit to top-N most-connected lemmas (matches other networks)
OUTPUT = "data/processed/wordnet_en_hyperedges.json"


def main():
    print(f"Loading {LEXICON}...")
    en = wn.Wordnet(lexicon=LEXICON)
    all_ss = list(en.synsets())
    print(f"  Total synsets: {len(all_ss)}")

    # --- Pass 1: collect all lemmas and count their synset memberships ---
    lemma_synset_count = defaultdict(int)
    for ss in all_ss:
        for sense in ss.senses():
            lemma = sense.word().lemma()
            lemma_synset_count[lemma] += 1

    print(f"  Unique lemmas: {len(lemma_synset_count)}")

    # Sort by connectivity (lemmas that appear in many synsets = more connected)
    ranked = sorted(lemma_synset_count.items(), key=lambda x: -x[1])
    top_lemmas = {lemma for lemma, _ in ranked[:TOP_N]}
    # Build lemma → integer ID
    lemma_to_id = {lemma: i for i, lemma in enumerate(sorted(top_lemmas))}
    print(f"  Top-{TOP_N} lemmas selected (max synset count: {ranked[0][1]})")

    # --- Pass 2: build hyperedges restricted to top_lemmas ---
    synset_hyperedges = []   # type 1: synset membership
    hypernymy_hyperedges = []  # type 2: child + parent synset members

    synsets_used = 0
    for ss in all_ss:
        members = []
        for sense in ss.senses():
            lemma = sense.word().lemma()
            if lemma in lemma_to_id:
                members.append(lemma_to_id[lemma])
        # Only keep hyperedges with ≥2 members (otherwise trivial)
        members = list(set(members))
        if len(members) >= 2:
            synset_hyperedges.append(sorted(members))
            synsets_used += 1

    print(f"  Synset hyperedges (≥2 top lemmas): {len(synset_hyperedges)}")

    # Hypernymy hyperedges
    for ss in all_ss:
        child_members = set()
        for sense in ss.senses():
            lemma = sense.word().lemma()
            if lemma in lemma_to_id:
                child_members.add(lemma_to_id[lemma])

        for parent in ss.hypernyms():
            parent_members = set()
            for sense in parent.senses():
                lemma = sense.word().lemma()
                if lemma in lemma_to_id:
                    parent_members.add(lemma_to_id[lemma])
            # Union hyperedge
            union = sorted(child_members | parent_members)
            if len(union) >= 2:
                hypernymy_hyperedges.append(union)

    print(f"  Hypernymy hyperedges (≥2 top lemmas): {len(hypernymy_hyperedges)}")

    # --- Also build pairwise projection (clique expansion of synset hyperedges) ---
    pairwise_edges = set()
    for he in synset_hyperedges + hypernymy_hyperedges:
        for i in range(len(he)):
            for j in range(i + 1, len(he)):
                pairwise_edges.add((he[i], he[j]))

    print(f"  Pairwise projection edges: {len(pairwise_edges)}")

    # --- Save ---
    node_list = sorted(top_lemmas)  # ID i → node_list[i]
    result = {
        "lexicon": LEXICON,
        "n_nodes": len(lemma_to_id),
        "nodes": {v: k for k, v in lemma_to_id.items()},  # id → lemma
        "synset_hyperedges": synset_hyperedges,
        "hypernymy_hyperedges": hypernymy_hyperedges,
        "pairwise_edges": [list(e) for e in sorted(pairwise_edges)],
        "stats": {
            "n_synset_hyperedges": len(synset_hyperedges),
            "n_hypernymy_hyperedges": len(hypernymy_hyperedges),
            "n_pairwise_edges": len(pairwise_edges),
            "mean_synset_size": (
                sum(len(h) for h in synset_hyperedges) / len(synset_hyperedges)
                if synset_hyperedges else 0
            ),
        },
    }

    with open(OUTPUT, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nSaved to {OUTPUT}")
    print(f"  Nodes: {result['n_nodes']}")
    print(f"  Synset hyperedges: {result['stats']['n_synset_hyperedges']}")
    print(f"  Hypernymy hyperedges: {result['stats']['n_hypernymy_hyperedges']}")
    print(f"  Mean synset size: {result['stats']['mean_synset_size']:.2f}")
    print(f"  Pairwise edges: {result['stats']['n_pairwise_edges']}")


if __name__ == "__main__":
    main()
