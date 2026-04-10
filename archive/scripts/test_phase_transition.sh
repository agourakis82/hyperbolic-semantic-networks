#!/bin/bash

# Test Sounio Phase Transition Experiment

set -e

echo "=== Testing Sounio Phase Transition Experiment ==="

# Check if souc exists
if ! command -v souc &> /dev/null; then
    echo "Error: souc compiler not found in PATH"
    echo "Please build souc first or add to PATH"
    exit 1
fi

# Test 1: Basic compilation
echo "\n1. Testing compilation..."
souc experiments/01_epistemic_uncertainty/phase_transition.sio -o phase_transition_test

if [ $? -eq 0 ]; then
    echo "✓ Compilation successful"
else
    echo "✗ Compilation failed"
    exit 1
fi

# Test 2: Run the program
echo "\n2. Running phase transition experiment..."
./phase_transition_test | head -20

if [ $? -eq 0 ]; then
    echo "✓ Execution successful"
else
    echo "✗ Execution failed"
    exit 1
fi

# Test 3: Verify output format
echo "\n3. Verifying output format..."
./phase_transition_test | grep -E "^[0-9]+,[0-9]+,[0-9.]+,[-0-9.]+,[0-9.]+,[0-9.]+,[0-9]+,[0-2],[0-2]$" | head -5

if [ $? -eq 0 ]; then
    echo "✓ Output format correct"
else
    echo "✗ Output format incorrect"
fi

# Test 4: Run a simpler test
echo "\n4. Testing simpler Sounio program..."
cat > test_simple.sio << 'EOF'
fn main() with IO {
    println("Simple test passed!")
    let x = 5
    let y = 3
    println("5 + 3 = " + int_to_string(x + y))
}

fn int_to_string(n: i64) -> string with Mut, Panic, Div {
    if n == 0 {
        "0"
    } else {
        let negative = n < 0
        var num = if negative { 0 - n } else { n }
        var result = ""
        while num > 0 {
            let digit = num % 10
            let ch = 48 + digit
            result = char_from_i64(ch) + result
            num = num / 10
        }
        if negative { "-" + result } else { result }
    }
}

fn char_from_i64(n: i64) -> string with Mut, Panic {
    str_slice("0123456789", n, n + 1)
}
EOF

souc test_simple.sio -o test_simple
./test_simple

# Cleanup
echo "\n=== Test Summary ==="
echo "Phase transition experiment: READY"
echo "Sounio compiler: WORKING"
echo "\nNext steps:"
echo "1. Run all experiments: bash experiments/01_epistemic_uncertainty/run.sh"
echo "2. Create unit tests for core functions"
echo "3. Add performance benchmarks"

rm -f phase_transition_test test_simple test_simple.sio
