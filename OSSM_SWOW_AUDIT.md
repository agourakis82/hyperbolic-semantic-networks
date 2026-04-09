# O-SSM × SWOW-EN Audit

Date: 2026-04-09  
Repository: `hyperbolic-semantic-networks`  
Canonical cross-repo reference: `/home/demetrios/work/sounio-lang` (`github.com/sounio-lang/sounio`)

## Scope

This audit answers the cross-repo questions for integrating an octonionic state
space model with the CPC 2026 SWOW-EN pipeline.

I treated `/home/demetrios/work/sounio-lang` as the canonical Sounio checkout,
per user instruction. The separate local checkout `/home/demetrios/work/sounio`
was not used as the source of truth for this report.

## Executive Summary

- I found **no explicit O-SSM implementation** in the canonical Sounio repo.
- I found **no repository evidence** for the claimed benchmark package
  (`ListOps`, `Bracket Matching`, `sMNIST`, `86K` params, or
  `"When Do Brackets Matter?"`) as runnable code.
- The canonical Sounio repo **does** contain:
  - mature octonion arithmetic,
  - tested non-associativity / associator machinery,
  - toy recurrent sequence functions in real-valued autograd,
  - octonion feedforward demos,
  - and a genuine hypercomplex training stack for **sedenion** embeddings.
- On the SWOW side, the CPC pipeline already provides enough per-node features
  to build an 8D octonionic input vector for the **438-node largest connected
  component**.
- The current CPC results are therefore best interpreted as:
  - **SWOW bridge mostly ready**, and
  - **O-SSM engine not yet materialized in canonical Sounio**.

---

## In `sounio-lang/sounio`

## 1. Where is the O-SSM implementation?

### Bottom line

I did **not** find a file that implements the requested octonionic state-space
equation

`h_{t+1} = σ(A · h_t · B + C · x_t)`

nor an octonionic BPTT stack, nor the benchmark tasks named in the prompt.

### Searches that came back negative

Repository-wide searches in `/home/demetrios/work/sounio-lang` found no
meaningful hits for:

- `O-SSM`
- `OSSM`
- `When Do Brackets Matter`
- `ListOps`
- `Bracket Matching`
- `sMNIST`
- `86K`

### Nearest reusable files I did find

These are the closest code artifacts to an eventual cognitive O-SSM, but they
are **not** the requested model.

#### A. Octonion feedforward demo

File: `examples/onn_rotation_prediction.sio`

What it is:
- A self-contained octonion feedforward demo for 3D rotation prediction.
- Uses octonion multiplication, octonion activations, and a toy training step.

Important callable surface:
- `fn network_forward(net: &RotationNetwork, input: Octonion) -> Octonion`
- `fn training_step(net: &!RotationNetwork, input: Octonion, target: Octonion, learning_rate: f32) -> f32`
- `fn main() -> i32 with Panic`

Parameterization actually present in code:
- `struct RotationNetwork { w1, b1, w2, b2: Octonion }`
- That is **4 octonions = 32 scalar floats** of live parameters.

What the file header claims:
- Input: 2 octonions
- Hidden: 4 octonions
- Output: 2 octonions
- `"72 semantic parameters = 576 floats in weight matrices"`

Audit interpretation:
- The comments describe a richer architecture than the code actually instantiates.
- The `training_step` is explicitly a **mock update**, not real backprop:
  it says “In production, this would use backpropagation via autodiff”.
- This file is useful as a syntax and octonion-API reference, but it is **not**
  an O-SSM.

#### B. Octonion MLP demo

File: `examples/octonion_nn_demo.sio`

What it is:
- A standalone 2-layer octonion MLP demonstration.

Important callable surface:
- `fn neuron_forward(weight: Octonion, bias: Octonion, input: Octonion) -> Octonion`
- `fn mlp2_forward(w1: Octonion, b1: Octonion, w2: Octonion, b2: Octonion, input: Octonion) -> Octonion`
- `fn main() -> i32`

Audit interpretation:
- Feedforward only.
- No sequence model, no hidden-state persistence, no BPTT.

#### C. Real-valued recurrent sequence helpers

File: `stdlib/nn/autograd.sio`

What it is:
- A large real-valued autodiff / neural-net utility file.
- Contains small recurrent helpers and fixed-length sequence processors.

Relevant callable surface:
- `fn rnn_sequence_3(x1: f64, x2: f64, x3: f64, h0: f64, w_ih: f64, w_hh: f64, bias: f64) -> RNNSeq3Result`
- `fn lstm_sequence_3(x1: f64, x2: f64, x3: f64, h0: f64, c0: f64, w: LSTMWeights) -> LSTMSeq3Result`
- `fn gru_sequence_3(x1: f64, x2: f64, x3: f64, h0: f64, w: GRUWeights) -> GRUSeq3Result`
- `fn ode_rnn_sequence(h0: f64, x1: f64, dt1: f64, x2: f64, dt2: f64, x3: f64, dt3: f64, w_ode1: f64, b_ode1: f64, w_ode2: f64, b_ode2: f64, w_hh: f64, w_xh: f64, b_h: f64) -> ODERNNSeqResult`

Audit interpretation:
- These are sequential and stateful, so they matter conceptually.
- But they are **scalar / real-valued toy helpers**, not octonionic state-space
  code and not benchmark experiments.

#### D. Hypercomplex training infrastructure that actually does backprop

Files:
- `stdlib/snn/sedenion_backward.sio`
- `stdlib/snn/sedenion_training.sio`

Important callable surface:
- `pub fn sed_mul_backward_a(grad_output: Sedenion, a: Sedenion, b: Sedenion) -> Sedenion`
- `pub fn sed_mul_backward_b(grad_output: Sedenion, a: Sedenion, b: Sedenion) -> Sedenion`
- `pub fn sed_train_triple_pair(model: &!SedenionKGModel, pos_head: i32, pos_rel: i32, pos_tail: i32, neg_head: i32, neg_rel: i32, neg_tail: i32, entity_optimizer: &!SedAdamOptimizer, relation_optimizer: &!SedAdamOptimizer, config: SedTrainingConfig) -> f32 with Panic, Mut`

Audit interpretation:
- This is the strongest evidence that canonical Sounio can support a genuine
  hypercomplex training loop.
- But it is for **sedenion knowledge graph embeddings**, not an octonion
  state-space sequence model.

### Benchmark task definitions

I found **no canonical runnable task definitions** for:

- ListOps
- Sorting benchmark in the O-SSM sense
- Bracket Matching
- sMNIST

There is a generic `examples/algo/sorting_demo.sio`, but it is unrelated to an
octonionic sequence benchmark suite.

### Answer

The canonical repo currently contains **supporting hypercomplex machinery**, but
not the requested O-SSM implementation as a recoverable, benchmarked code path.

---

## 2. What octonionic arithmetic is available in Sounio's stdlib?

### Core arithmetic available

#### `stdlib/math/octonion.sio`

Implemented:
- `fn oct(...) -> Octonion`
- `fn oct_conj(o: Octonion) -> Octonion`
- `fn oct_norm_sq(o: Octonion) -> f32`
- `fn oct_norm(o: Octonion) -> f32`
- `fn oct_normalize(o: Octonion) -> Octonion with Panic`
- `fn oct_inv(o: Octonion) -> Octonion with Panic`
- `fn oct_relu(o: Octonion) -> Octonion`
- `fn oct_sigmoid(o: Octonion) -> Octonion`
- `fn oct_tanh(o: Octonion) -> Octonion`
- `fn oct_real(o: Octonion) -> f32`
- `fn oct_dot(o1: Octonion, o2: Octonion) -> f32`
- `fn oct_mul(a: Octonion, b: Octonion) -> Octonion`
- quaternion-decomposition helpers:
  - `fn oct_to_quaternion_parts(o: Octonion) -> OctonionParts`
  - `fn oct_from_quaternion_parts(p: OctonionParts) -> Octonion`

#### `stdlib/nn/octonion.sio`

Implemented helper operations:
- `fn oct_zero() -> Octonion`
- `fn oct_one() -> Octonion`
- `fn oct_add(a: Octonion, b: Octonion) -> Octonion`
- `fn oct_sub(a: Octonion, b: Octonion) -> Octonion`
- `fn oct_scale(v: Octonion, s: f32) -> Octonion`
- `fn oct_imag_norm_sq(o: Octonion) -> f32`
- `fn oct_imag_norm(o: Octonion) -> f32`
- `fn oct_rotate(u: Octonion, v: Octonion) -> Octonion`

#### `self-hosted/hypercomplex/octonion.sio`

Implemented in the self-hosted f64 path:
- `fn oct_conjugate(o: Oct) -> Oct`
- `fn oct_norm_squared(o: Oct) -> f64`
- `fn oct_norm(o: Oct) -> f64`
- `fn oct_normalize(o: Oct) -> Oct`
- `fn oct_mul(a: Oct, b: Oct) -> Oct`
- `fn oct_inverse(o: Oct) -> Oct`
- `fn oct_mul_cayley_dickson(p: Oct, q: Oct) -> Oct`
- `fn oct_associator(a: Oct, b: Oct, c: Oct) -> Oct`

### What is tested

Test coverage exists in:
- `tests/run-pass/octonion_basic_ops.sio`
- `tests/run-pass/octonion_basic_ops_standalone.sio`
- `tests/run-pass/octonion_cayley_dickson.sio`
- `tests/run-pass/octonion_basic_demo.sio`
- `tests/stdlib/math/test_hyper_math_e2e.sio`
- `tests/stdlib/onn/test_hyper_onn_e2e.sio`
- `self-hosted/hypercomplex/test_octonion.sio`

The self-hosted test file explicitly checks:
- identity,
- `e_i^2 = -1`,
- Fano-plane multiplication,
- anti-commutativity,
- non-associativity,
- alternativity,
- norm multiplicativity,
- conjugate product,
- Cayley-Dickson consistency.

### What is missing

I did **not** find canonical implementations of:
- Wirtinger derivatives for octonions,
- octonion-specific reverse-mode autodiff,
- octonion BPTT,
- octonion Jacobian / state-space training utilities.

### Answer

Canonical Sounio has **solid octonion algebra** and **tested associator
machinery**, but **not** the derivative machinery needed to claim an existing
octonion sequence-learning stack.

---

## 3. What is the O-SSM's input interface?

### Bottom line

There is **no existing O-SSM input interface** to audit, because there is no
existing O-SSM in the canonical repo.

### What the repo does support

#### Single-octonion inputs

Files:
- `examples/octonion_nn_demo.sio`
- `examples/onn_rotation_prediction.sio`

These demos take one `Octonion` at a time as input to feedforward layers.

#### Fixed-length sequential inputs

File:
- `stdlib/nn/autograd.sio`

The sequence helpers there are:
- fixed-length,
- explicitly unrolled,
- scalar / real-valued,
- and not graph-aware.

They process 3-step sequences such as:
- `rnn_sequence_3(...)`
- `lstm_sequence_3(...)`
- `gru_sequence_3(...)`
- `ode_rnn_sequence(...)`

#### Graph-structured input

Files:
- `stdlib/data/io.sio`
- `stdlib/data/csv_loader.sio`

Relevant callable surface:
- `pub fn read_csv(text: String, options: CsvOptions) -> DataFrame`
- `pub fn read_csv_simple(text: String) -> DataFrame`
- `pub fn parse_edge_list(csv_content: string) -> NetworkData with Mut, Div, Panic`

Important limitation:
- `data/csv_loader.sio` parses CSV **content strings** into graph data.
- `load_edge_list(filepath: string)` is currently stubbed.
- In the canonical repo, file I/O exists through `read_file(...)` in the
  self-hosted runtime, so a self-hosted experiment can still load text from
  disk and pass it into the CSV parser.

### Answer

The canonical repo currently supports:
- single-octonion feedforward inputs,
- toy fixed-length scalar sequences,
- and CSV graph parsing from text,

but **not** a graph-structured octonionic recurrent input pipeline.

---

## 4. What are the O-SSM hyperparameters from the benchmark experiments?

### Bottom line

I found **no benchmark experiment suite** in the canonical repo that can
justify the requested hyperparameters:

- hidden dimension,
- number of octonionic units,
- learning rate,
- BPTT truncation length,
- or total parameter count `≈ 86K`.

### What can be grounded from the repo

#### `examples/onn_rotation_prediction.sio`

Documented in file comments:
- input: 2 octonions,
- hidden: 4 octonions,
- output: 2 octonions,
- `"72 semantic parameters = 576 floats in weight matrices"`.

But the instantiated code actually defines:
- `struct RotationNetwork { w1, b1, w2, b2: Octonion }`
- so the executable parameter surface is only **4 octonions = 32 scalar floats**.

#### `stdlib/snn/sedenion_training.sio`

Default training config exists for sedenion KG embeddings:
- `learning_rate = 0.001`
- `max_epochs = 100`
- `batch_size = 128`
- `margin = 1.0`
- `zero_divisor_penalty = 0.001`
- `grad_clip_norm = 5.0`
- `patience = 10`

Audit interpretation:
- These are real hyperparameters in canonical Sounio.
- But they belong to the **sedenion embedding trainer**, not to an O-SSM.

### Answer

The canonical repo does **not** currently support the claim that an `86K`
O-SSM benchmark package already exists there. Those hyperparameters need to be
treated as **external-to-repo until independently supplied**.

---

## In `agourakis82/hyperbolic-semantic-networks`

## 5. What per-node features are available?

### Existing CPC per-node artifacts

#### `results/cpc2026/node_metrics.parquet`

Shape:
- 438 rows

Columns:
- `node`
- `degree`
- `strength`
- `entropy`
- `entropy_norm`
- `kappa`
- `C_ent`

Interpretation:
- This is the primary CPC node-metric table.
- It already contains the core geometric quantities needed for O-SSM input.

#### `data/processed/swow_en_valence.csv`

Shape:
- 438 rows

Columns:
- `node`
- `word`
- `matched_warriner`
- `valence_raw`
- `valence_centered`
- `arousal_raw`
- `dominance_raw`

Interpretation:
- Valence is already present.
- Arousal and dominance are already present too, so the bridge does **not**
  need to re-download Warriner just to get those dimensions.

#### `results/cpc2026/poincare_embedding.parquet`

Shape:
- 438 rows

Columns:
- `node`
- `x`
- `y`
- `radius`
- `embedding_engine`

Interpretation:
- There is already a 2D Poincare embedding for exactly the same 438 nodes.
- The current embedding engine is `gensim_poincare`.

#### `data/semantic_flow/swow_en_embedding.csv`

Shape:
- 438 rows

Columns:
- `node`
- `x`
- `y`
- `z`

Interpretation:
- There is also a separate 3D embedding artifact.
- The CPC pipeline itself currently uses the Poincare artifact in
  `results/cpc2026/`, not this older semantic-flow file.

#### `results/unified/swow_en_exact_lp.json`

What it contains:
- exact LP SWOW-EN curvature summary,
- `N = 438`,
- `E = 640`,
- `per_edge_curvatures` of length 640.

Important limitation:
- This file is **per-edge**, not per-node.
- The per-node `kappa` values used by CPC were reconstructed in the CPC Python
  layer and written to `node_metrics.parquet`.

### Coverage alignment

The following CPC artifacts have exactly the same node coverage:
- `node_metrics.parquet`: 438 nodes
- `swow_en_valence.csv`: 438 nodes
- `poincare_embedding.parquet`: 438 nodes

Shared node intersection:
- 438 / 438 / 438

### Available numeric feature space right now

Immediately mergeable numeric node dimensions:
- `degree`
- `strength`
- `entropy`
- `entropy_norm`
- `kappa`
- `C_ent`
- `valence_centered`
- `arousal_raw`
- `dominance_raw`
- `x`
- `y`
- `radius`

Total immediately available numeric dimensions:
- **12**

### Missing dimension relative to the proposed 8D octonionic input

Missing only from the exact proposed vector:
- `η_local(v) = <k_local>^2 / N_local`

Audit interpretation:
- That term is **computable from the graph** and does not require external data.

### Answer

The hyperbolic repo already contains all core per-node features needed for an
8D octonionic node representation, except `η_local(v)`, which can be computed
directly from the SWOW graph.

---

## 6. What is the actual SWOW-EN graph size?

### Raw SWOW-EN

Raw SWOW is **not committed** in this repo.

`data/raw/DATA_DOWNLOAD.md` states:
- raw SWOW must be downloaded separately,
- the English raw source is `strength.SWOW-EN.R1.20180827.csv`.

The root `README.md` also references an English SWOW dataset of `10,571` nodes,
but that full raw graph is **not present in git** here.

### Processed English graph variants actually present in-repo

#### A. `data/processed/english_edges.csv`

Computed graph stats:
- 500 nodes
- 13,495 undirected edges
- 1 connected component

Interpretation:
- Dense processed English variant.

#### B. `data/processed/english_edges_R1.csv`

Computed graph stats:
- 500 nodes
- 5,465 undirected edges
- 1 connected component

Interpretation:
- Another 500-node processed variant, sparser than `english_edges.csv`.

#### C. `data/processed/english_edges_FINAL.csv`

Computed graph stats:
- 467 nodes
- 661 undirected edges
- 11 connected components
- largest connected component = 438 nodes

Why this matters:
- This is the graph the CPC pipeline currently uses.
- After largest-component restriction, the CPC run operates on:
  - `N = 438`
  - `E = 640`

### Clarified answer

There is no single “actual SWOW-EN graph size” in the current repo checkout.
There are **three distinct processed English variants**:

- a dense 500-node graph,
- a medium-density 500-node graph,
- and a sparse 467-node graph whose LCC is 438 nodes.

For the CPC pipeline specifically, the operative answer is:

- **SWOW-EN used in CPC = LCC of `english_edges_FINAL.csv` = 438 nodes / 640 edges**

For the broader project narrative:

- the full `10,571`-node English SWOW graph is cited in documentation,
- but it is **not available as a committed local artifact** in this repo.

---

## 7. What Markov chain results exist as baseline?

Baseline source:
- `results/cpc2026/statistical_summary.json`

### Regime means

| Regime | Mean Var(`C_ent`) | Mean Residence in Top-10% Entropy Hubs | Mean Entropy Production | Mean Hurst |
|---|---:|---:|---:|---:|
| normative | 0.0174742 | 0.1414476 | 0.68906 | 0.74988 |
| anxious | 0.0146196 | 0.1854090 | 0.60599 | 0.86216 |
| ruminative | 0.01188 | 0.12118 | 0.66756 | 0.48029 |
| psychotic | 0.00919 | 0.23789 | 0.60518 | 0.83139 |

### Headline comparison numbers

#### Normative vs anxious `C_ent` variance

- Cohen's `d = -0.26588450227800453`
- 95% bootstrap CI:
  - `[-0.28981890047915704, -0.24249784423040882]`
- `p = 7.1669623893164555e-78`

Interpretation:
- The current Markov baseline separates the regimes,
- but in the opposite direction from the original poster-era projection.

#### Normative vs anxious high-entropy-hub residence

- anxious mean = `0.1854090`
- normative mean = `0.1414476`
- percent increase = `31.07963655799042`
- 95% bootstrap CI on percent increase:
  - `[28.526067161186717, 33.553074910382186]`
- `p = 0.0`

#### Phase-reference values used in CPC validation

- `eta_critical_reference = 2.939427214662331`
- `swow_eta = 0.019498338594933346`
- `swow_position = deep_hyperbolic_subcritical`

### Answer

The current CPC baseline is a fully materialized **biased Markov-chain** result
set, and these are the numbers any O-SSM replacement or complement must be
compared against.

---

## Practical Consequence For Implementation

The honest implementation path is:

1. Treat `/home/demetrios/work/sounio-lang` as the canonical Sounio repo.
2. Treat canonical Sounio as providing:
   - octonion algebra,
   - associator machinery,
   - toy recurrent sequence patterns,
   - and hypercomplex training examples,
   but **not** a finished O-SSM.
3. Treat `results/cpc2026/node_metrics.parquet`,
   `data/processed/swow_en_valence.csv`, and
   `results/cpc2026/poincare_embedding.parquet` as the ready-made SWOW bridge.
4. Build the bridge and cognitive experiment as **new code**:
   - not as a thin wrapper around a pre-existing canonical O-SSM.

## Bottom Line

The SWOW side of the project is already in good shape for an octonionic bridge.
The Sounio side is **close in ingredients but not in finished architecture**.

So the correct framing is:

- **we can implement an O-SSM-style cognitive dynamics experiment now,**
- but it will be a **new canonical experiment built on existing octonion and
  hypercomplex primitives**, not a recovered benchmark package that already
  exists in `sounio-lang/sounio`.
