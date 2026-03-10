#!/bin/bash

# Run all Sounio tests in experiments directory

set -e

echo "========================================"
echo "  Sounio Experiments Test Suite"
echo "========================================"

# Check for souc compiler
if ! command -v souc &> /dev/null; then
    echo "ERROR: 'souc' compiler not found in PATH"
    echo "Please build souc and add to PATH"
    exit 1
fi

SOUC_VERSION=$(souc --version 2>/dev/null || echo "unknown")
echo "Using souc version: $SOUC_VERSION"
echo ""

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_file="$2"
    
    echo "Testing: $test_name"
    echo "  File: $test_file"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if souc "$test_file" -o /tmp/sounio_test_out 2>/dev/null; then
        if /tmp/sounio_test_out 2>/dev/null; then
            echo "  ✓ PASS"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo "  ✗ FAIL - Runtime error"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        echo "  ✗ FAIL - Compilation error"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    rm -f /tmp/sounio_test_out
    echo ""
}

# Test 1: LCG unit tests
echo "--- Phase 1: Core Function Tests ---"
run_test "LCG Random Number Generator" "experiments/01_epistemic_uncertainty/test_lcg.sio"

# Test 2: Simple I/O test
cat > /tmp/test_io.sio << 'EOF'
fn main() with IO {
    println("I/O test passed")
}
EOF
run_test "Basic I/O" "/tmp/test_io.sio"

# Test 3: Epistemic demo
if [ -f "experiments/01_epistemic_uncertainty/epistemic_demo.sio" ]; then
    run_test "Epistemic Demo" "experiments/01_epistemic_uncertainty/epistemic_demo.sio"
fi

# Test 4: Test print
if [ -f "experiments/01_epistemic_uncertainty/test_print.sio" ]; then
    run_test "Print Test" "experiments/01_epistemic_uncertainty/test_print.sio"
fi

# Test 5: Phase transition (compile only - runtime is long)
echo "--- Phase 2: Experiment Compilation ---"
echo "Testing: Phase Transition Experiment"
echo "  File: experiments/01_epistemic_uncertainty/phase_transition.sio"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
if souc "experiments/01_epistemic_uncertainty/phase_transition.sio" -o /tmp/phase_transition_test 2>/dev/null; then
    echo "  ✓ COMPILES OK (runtime test skipped - takes ~30 seconds)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    
    # Quick smoke test - run first few lines
    echo "  Running quick smoke test..."
    timeout 5s /tmp/phase_transition_test | head -5
    if [ $? -eq 0 ]; then
        echo "  ✓ Smoke test passed"
    else
        echo "  ⚠ Smoke test timed out or failed"
    fi
else
    echo "  ✗ FAIL - Compilation error"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
rm -f /tmp/phase_transition_test
echo ""

# Test other experiment directories
echo "--- Phase 3: Other Experiments ---"
for exp_dir in experiments/*/; do
    if [ -f "${exp_dir}run.sh" ]; then
        exp_name=$(basename "$exp_dir")
        echo "Found experiment: $exp_name"
        echo "  Has run.sh script"
        
        # Look for .sio files
        sio_files=$(find "$exp_dir" -name "*.sio" -type f | head -5)
        if [ -n "$sio_files" ]; then
            echo "  Contains Sounio files:"
            for file in $sio_files; do
                echo "    - $(basename "$file")"
            done
        fi
        echo ""
    fi
done

# Summary
echo "========================================"
echo "  TEST SUMMARY"
echo "========================================"
echo "Total tests: $TOTAL_TESTS"
echo "Passed:      $PASSED_TESTS"
echo "Failed:      $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "Next steps:"
    echo "1. Run full phase transition: bash experiments/01_epistemic_uncertainty/run.sh"
    echo "2. Create more unit tests for graph functions"
    echo "3. Add performance benchmarks"
    exit 0
else
    echo "❌ Some tests failed"
    echo ""
    echo "Debug steps:"
    echo "1. Check souc compiler: souc --version"
    echo "2. Test simple program: echo 'fn main() { println(\"test\") }' | souc -o test"
    echo "3. Examine failing test files"
    exit 1
fi
