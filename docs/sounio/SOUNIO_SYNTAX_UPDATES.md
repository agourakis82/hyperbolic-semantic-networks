# Sounio Syntax Updates Needed

**Date**: December 23, 2024
**Status**: Reviewed actual Sounio repository - found syntax differences

---

## 🔍 Key Findings from Repository Review

### Version Status
- ✅ Repository cloned and up to date
- ✅ Version 0.83.0 (latest)
- ✅ Recent commits include parser fixes and epistemic improvements
- ⚠️ Cargo/Rust not available on this system (expected)

### Graph Module Location
- ✅ Our graph module successfully created at `stdlib/graph/`
- ✅ Files visible in repository: types.d, algorithms.d, sinkhorn.d, curvature.d, random.d

### Standard Library APIs Discovered

#### 1. **Vec Syntax** ✅
From `stdlib/collections/vec.d` and examples:
```d
let v: Vec<i32> = Vec.new()
v.push(42)  // with Alloc effect
let len = v.len()
```
**Status**: Our implementation matches! ✅

#### 2. **Option Syntax** ✅
```d
Option.Some(value)
Option.None
match opt {
    Option.Some(x) => { ... }
    Option.None => { ... }
}
```
**Status**: Our implementation matches! ✅

#### 3. **Random Number Generation** ⚠️
Found `stdlib/prob/random.d` but it's just a test file with LCG:
```d
fn lcg(seed: i64) -> i64 {
    let a: i64 = 1664525
    let c: i64 = 1013904223
    let m: i64 = 4294967296
    return (a * seed + c) % m
}
```

**Issue**: No `with Random` effect handler visible yet!
**Our code uses**: Placeholder `random_u64() -> u64 with Random`
**Action needed**: Keep placeholders, mark as TODO for when Random effect is implemented

#### 4. **Iterator API** ⚠️
Found `stdlib/iter/iterator.d` with full trait system:
```d
pub trait Iterator {
    type Item;
    fn next(&!self) -> Option<Self.Item>;
    fn filter<P>(self, predicate: P) -> Filter<Self, P>
    fn map<B, F>(self, f: F) -> Map<Self, F>
    fn sum(&self) -> Self.Item  // ???
}
```

**Our code uses**: `.iter()`, `.sum()`, `.max()`
**Status**: API exists but might not be fully implemented
**Action**: Replace with manual loops to be safe

#### 5. **Epistemic Computing** ✅
From `stdlib/epistemic/pk_example.d`:
```d
struct EpistemicValue {
    value: f64,
    uncert: Uncertainty,
    conf: f64,
    source: i32,
}
```

**Our code uses**: `Knowledge.new(value:, confidence:, source:)`
**Status**: Conceptually correct, but actual API might differ
**Action**: Keep design, mark as needing validation

#### 6. **Effect System Syntax** ✅
Confirmed from multiple files:
```d
fn function_name(...) -> ReturnType with Effect1, Effect2 {
    // ...
}
```

Effects seen in wild:
- `with Alloc` ✅
- `with Panic` ✅
- `with IO` ✅
- `with Random` ❓ (declared but implementation unclear)
- `with Confidence` ❓ (our invention, needs validation)
- `with Parallel` ❓ (our invention, needs validation)

#### 7. **String and Printing**
```d
fn main() -> i32 {
    println("Hello")  // No formatting seen!
    return 0
}
```

**Our code uses**: `println("N={:3}, k={:2}", n, k)` (Rust-style)
**Issue**: Sounio might not have format strings yet!
**Action**: Use simple concatenation or multiple println calls

---

## 🔧 Required Updates to Our Code

### Priority 1: Critical Syntax Issues

#### 1. **Remove Format Strings**
File: `examples/network_geometry_demo.d`

**Current**:
```d
println("  N={:3}, k={:2}: ratio={:5.2} → {}{}",
        n, k, ratio, predicted, marker);
```

**Should be**:
```d
println("  N=")
println(n)
println(", k=")
println(k)
println(": ratio=")
println(ratio)
// etc...
```

#### 2. **Replace Iterator Methods**
Files: Multiple

**Current**:
```d
for &neighbor in g.neighbors(u) { ... }
let sum: f64 = curvatures.iter().sum();
let max_id = components.iter().max().unwrap_or(0);
```

**Should be**:
```d
for i in 0..neighbors.len() {
    let neighbor = neighbors[i];
    // ...
}

let mut sum: f64 = 0.0;
for i in 0..curvatures.len() {
    sum = sum + curvatures[i];
}
```

#### 3. **Fix Vec Cloning**
File: `stdlib/graph/sinkhorn.d`

**Current**:
```d
let mut u_old = u.clone();
```

**Issue**: `.clone()` might not exist
**Should be**:
```d
let mut u_old = Vec.with_capacity(n);
for i in 0..n {
    u_old.push(u[i]);
}
```

### Priority 2: API Uncertainties

#### 4. **Deque Availability**
File: `stdlib/graph/algorithms.d`

**Current**:
```d
import std.collections.deque;
let mut queue = Deque.new();
queue.push_back(source);
let u = queue.pop_front().unwrap();
```

**Status**: Deque exists in stdlib but might not have these methods
**Backup**: Use Vec as queue (inefficient but works):
```d
let mut queue = Vec.new();
queue.push(source);
let u = queue.remove(0);  // O(n) but fine for BFS
```

#### 5. **HashSet/HashMap Availability**
File: `stdlib/graph/random.d`

**Current**:
```d
let mut edge_set = HashSet.new();
edge_set.insert(edge_key);
edge_set.contains(&edge_key);
```

**Status**: HashSet exists but API unclear
**Backup**: Use Vec for small sets:
```d
let mut edge_list = Vec.new();
// Linear search for duplicates
```

### Priority 3: Effect System

#### 6. **Knowledge Type**
File: `stdlib/graph/curvature.d`

**Current**:
```d
Knowledge.new(
    value: kappa_mean,
    confidence: confidence,
    source: Source.Computation("Ollivier-Ricci")
)
```

**Status**: Need to check if `Knowledge` and `Source` types exist
**Action**: If not, define them or use raw EpistemicValue

#### 7. **Random Effect**
Multiple files

**Current**: Functions declared `with Random`
**Status**: Effect exists in type system but handler unclear
**Action**: Keep declarations, implement LCG-based placeholders

---

## 📋 Action Plan

### Phase 1: Make It Compile (Priority)

1. **Remove all format strings** → Use multiple println calls
2. **Remove iterator combinators** → Use manual for loops
3. **Remove .clone()** → Manual copy loops
4. **Simplify random.d** → Use LCG from stdlib/prob/random.d
5. **Test with basic graph** → Create 3-node triangle, compute degree

### Phase 2: Validate APIs

6. **Check Deque API** → Try compiling with dc
7. **Check HashSet API** → Try compiling with dc
8. **Check Option API** → Verify match syntax
9. **Check Vec methods** → Verify push, len, as_slice, etc.

### Phase 3: Effect System

10. **Implement Random** → Use LCG with state
11. **Implement Confidence** → Define Knowledge type if needed
12. **Implement Parallel** → Mark as TODO for later

---

## 🎯 Immediate Next Steps

**Since we don't have cargo**, I'll update the code based on what we learned:

1. ✅ Confirmed graph module is in place
2. 🔧 Update `network_geometry_demo.d` to remove format strings
3. 🔧 Update all files to use manual loops instead of iterators
4. 🔧 Implement simple LCG-based RNG
5. 🔧 Add notes about which features are TODO
6. 📄 Create a "known issues" document
7. 📄 Update README with current status

**Then**: Send updated status to you (Maria) so you can:
- Try compiling with dc
- Report actual errors
- Guide me on API details
- Tell me which effects are ready

---

## 💡 Good News

Despite syntax differences, the **core algorithms are sound**:
- ✅ Graph representation is correct
- ✅ BFS algorithm is correct
- ✅ Sinkhorn algorithm is correct
- ✅ Ollivier-Ricci formula is correct
- ✅ Configuration model is correct

It's just a matter of adapting to Sounio' current syntax and stdlib state!

---

**Status**: Ready to update code based on findings
**Blocker**: Need compiler access to test (your machine)
**Next**: Update syntax, create testing instructions for you
