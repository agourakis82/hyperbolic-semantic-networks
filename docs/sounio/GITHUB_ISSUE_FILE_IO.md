# GitHub Issue: File I/O and CSV Parsing Support

**Repository**: sounio (to be posted)  
**Title**: Feature Request: File I/O and CSV Parsing for Data Loading  
**Labels**: enhancement, stdlib, io

---

## Summary

Request for basic file I/O operations and CSV parsing capabilities in Sounio's standard library to enable loading external datasets without preprocessing.

---

## Motivation

**Use Case**: Scientific computing with real-world datasets

I'm using Sounio to validate Ollivier-Ricci curvature computations on semantic networks (SWOW dataset). Currently, I need to preprocess CSV files into hardcoded Sounio arrays, which is cumbersome for:

1. **Iterative development**: Every data change requires regenerating `.sio.inc` files
2. **Multiple datasets**: Testing 4 languages × 3 versions = 12 preprocessing runs
3. **Reproducibility**: External users can't easily run experiments with their own data

**Current Workaround**:
```python
# Python preprocessing script
python preprocess_swow_for_sounio.py spanish
# Generates: swow_spanish_edges.sio.inc (13,150 lines)
```

**Desired Workflow**:
```sounio
// Direct data loading in Sounio
let edges = read_csv("data/spanish_edges.csv") with IO;
let graph = build_from_edges(edges);
```

---

## Proposed Features

### 1. Basic File I/O

```sounio
// Read entire file as string
fn read_file(path: str) -> str with IO, Panic;

// Read file line by line
fn read_lines(path: str) -> [str; MAX_LINES] with IO, Panic;

// Write string to file
fn write_file(path: str, content: str) with IO, Panic;
```

**Example**:
```sounio
fn main() with IO, Panic {
    let content = read_file("data.txt");
    println(content);
}
```

### 2. CSV Parsing

```sounio
struct CsvRow {
    fields: [str; MAX_COLS],
    len: usize,
}

struct CsvData {
    rows: [CsvRow; MAX_ROWS],
    n_rows: usize,
    n_cols: usize,
}

// Parse CSV file
fn parse_csv(path: str, skip_header: bool) -> CsvData with IO, Panic;

// Parse CSV string
fn parse_csv_string(content: str) -> CsvData with Panic;
```

**Example**:
```sounio
fn main() with IO, Panic {
    let csv = parse_csv("edges.csv", true);  // Skip header
    
    let mut i = 0;
    while i < csv.n_rows {
        let source = csv.rows[i].fields[0];
        let target = csv.rows[i].fields[1];
        let weight = parse_f64(csv.rows[i].fields[2]);
        
        // Process edge...
        
        i = i + 1;
    }
}
```

### 3. String Utilities (Supporting Functions)

```sounio
// String parsing
fn parse_i64(s: str) -> i64 with Panic;
fn parse_f64(s: str) -> f64 with Panic;
fn parse_usize(s: str) -> usize with Panic;

// String manipulation
fn split(s: str, delimiter: str) -> [str; MAX_PARTS] with Panic;
fn trim(s: str) -> str;
fn contains(s: str, substring: str) -> bool;
```

---

## Design Considerations

### Fixed-Size Arrays
Since Sounio uses fixed-size arrays, file I/O functions need compile-time size limits:

```sounio
// Option 1: Hardcoded limits in stdlib
const MAX_FILE_SIZE: usize = 1048576;  // 1 MB
const MAX_LINES: usize = 10000;
const MAX_CSV_ROWS: usize = 10000;
const MAX_CSV_COLS: usize = 100;

// Option 2: User-specified limits (generic-like)
fn read_lines<const N: usize>(path: str) -> [str; N] with IO, Panic;
```

### Error Handling
File operations should use Sounio's effect system:

```sounio
fn read_file(path: str) -> str with IO, Panic {
    // Panics if file not found or read error
}

// Future: Result type for recoverable errors
fn try_read_file(path: str) -> Result<str, IOError> with IO {
    // Returns Err if file not found
}
```

### Performance
- **Lazy loading**: Don't load entire file if only parsing needed
- **Streaming**: For large files, consider line-by-line iteration
- **Zero-copy**: Minimize string allocations during parsing

---

## Implementation Phases

### Phase 1: Basic File I/O (MVP)
- `read_file(path: str) -> str`
- `write_file(path: str, content: str)`
- `read_lines(path: str) -> [str; MAX_LINES]`

### Phase 2: String Utilities
- `split(s: str, delimiter: str)`
- `parse_i64`, `parse_f64`, `parse_usize`
- `trim`, `contains`

### Phase 3: CSV Parsing
- `parse_csv(path: str, skip_header: bool)`
- `CsvRow`, `CsvData` structs

### Phase 4: Advanced Features (Future)
- Binary file I/O
- JSON parsing
- Streaming/iterator-based file reading

---

## Alternatives Considered

### 1. External Preprocessing (Current)
**Pros**: Works today  
**Cons**: Breaks workflow, not user-friendly, limits reproducibility

### 2. FFI to Rust/C
**Pros**: Full control, performance  
**Cons**: Defeats purpose of pure Sounio, adds complexity

### 3. Compile-Time File Inclusion
```sounio
const DATA: str = include_str!("data.csv");
```
**Pros**: Simple, no runtime I/O  
**Cons**: Bloats binary, can't load dynamic data

---

## Impact on Existing Code

**Breaking changes**: None (new stdlib functions only)

**Migration**: Existing preprocessing workflows continue to work

---

## Real-World Example

**Current** (with preprocessing):
```bash
# Step 1: Preprocess (Python)
python preprocess_swow_for_sounio.py spanish
# Generates: swow_spanish_edges.sio.inc (13,150 lines)

# Step 2: Include in Sounio
# load_swow_spanish.sio
let EDGES: [(usize, usize); 13150] = [
    (0, 1), (0, 2), ... // 13,150 lines
];
```

**Proposed** (with file I/O):
```sounio
// load_swow_spanish.sio
fn main() with IO, Panic, Div {
    let csv = parse_csv("../../data/processed/spanish_edges.csv", true);
    
    let mut edges: [(usize, usize); 15000] = [(0, 0); 15000];
    let mut n_edges = 0;
    
    let mut i = 0;
    while i < csv.n_rows {
        let u = parse_usize(csv.rows[i].fields[0]);
        let v = parse_usize(csv.rows[i].fields[1]);
        edges[n_edges] = (u, v);
        n_edges = n_edges + 1;
        i = i + 1;
    }
    
    let graph = build_from_edges(edges, n_edges, 500);
    // ... compute curvature
}
```

---

## References

- **Project**: Hyperbolic Semantic Networks (scientific computing)
- **Dataset**: SWOW (Small World of Words) - 4 languages, ~500 nodes each
- **Use case**: Ollivier-Ricci curvature validation
- **Sounio version**: 1.0.0-beta

---

## Questions for Maintainers

1. Is file I/O planned for Sounio stdlib?
2. What's the preferred approach for fixed-size limits (hardcoded vs. user-specified)?
3. Should CSV parsing be in stdlib or a separate library?
4. Any concerns about adding `IO` effect to more stdlib functions?

---

**Thank you for considering this feature request!** File I/O would make Sounio much more practical for scientific computing and data analysis workflows.

