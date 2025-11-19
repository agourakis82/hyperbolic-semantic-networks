#!/usr/bin/env python3
"""
Static analysis of Python codebase.

Runs:
- pylint for code quality
- mypy for type checking
- bandit for security
- Complexity analysis
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
import ast
import astor

def run_pylint(code_dir: Path):
    """Run pylint on codebase."""
    print("Running pylint...")
    
    try:
        result = subprocess.run(
            ['pylint', '--output-format=json', str(code_dir)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            issues = []
        else:
            try:
                issues = json.loads(result.stdout)
            except:
                issues = [{'message': result.stdout}]
        
        return {
            'tool': 'pylint',
            'exit_code': result.returncode,
            'issues': issues,
            'summary': {
                'total_issues': len(issues),
                'by_type': {}
            }
        }
    except FileNotFoundError:
        return {
            'tool': 'pylint',
            'error': 'pylint not installed',
            'install': 'pip install pylint'
        }
    except subprocess.TimeoutExpired:
        return {
            'tool': 'pylint',
            'error': 'Timeout after 300 seconds'
        }

def run_mypy(code_dir: Path):
    """Run mypy for type checking."""
    print("Running mypy...")
    
    try:
        result = subprocess.run(
            ['mypy', '--show-error-codes', '--no-error-summary', str(code_dir)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        errors = []
        for line in result.stdout.split('\n'):
            if line.strip() and 'error' in line.lower():
                errors.append(line.strip())
        
        return {
            'tool': 'mypy',
            'exit_code': result.returncode,
            'errors': errors,
            'summary': {
                'total_errors': len(errors)
            }
        }
    except FileNotFoundError:
        return {
            'tool': 'mypy',
            'error': 'mypy not installed',
            'install': 'pip install mypy'
        }
    except subprocess.TimeoutExpired:
        return {
            'tool': 'mypy',
            'error': 'Timeout after 300 seconds'
        }

def run_bandit(code_dir: Path):
    """Run bandit for security issues."""
    print("Running bandit...")
    
    try:
        result = subprocess.run(
            ['bandit', '-r', '-f', 'json', str(code_dir)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        try:
            issues = json.loads(result.stdout)
        except:
            issues = {'errors': [result.stdout]}
        
        return {
            'tool': 'bandit',
            'exit_code': result.returncode,
            'issues': issues
        }
    except FileNotFoundError:
        return {
            'tool': 'bandit',
            'error': 'bandit not installed',
            'install': 'pip install bandit'
        }
    except subprocess.TimeoutExpired:
        return {
            'tool': 'bandit',
            'error': 'Timeout after 300 seconds'
        }

def analyze_complexity(code_dir: Path):
    """Analyze code complexity using AST."""
    print("Analyzing code complexity...")
    
    complexity_results = []
    
    for py_file in code_dir.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(py_file))
            
            # Count complexity metrics
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count branches (if, for, while, etc.)
                    branches = sum(1 for n in ast.walk(node) 
                                 if isinstance(n, (ast.If, ast.For, ast.While, ast.Try)))
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'branches': branches,
                        'complexity': branches + 1
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno
                    })
            
            if functions or classes:
                complexity_results.append({
                    'file': str(py_file.relative_to(code_dir)),
                    'functions': functions,
                    'classes': classes,
                    'max_complexity': max([f['complexity'] for f in functions], default=0),
                    'high_complexity_functions': [f for f in functions if f['complexity'] > 10]
                })
        except Exception as e:
            complexity_results.append({
                'file': str(py_file.relative_to(code_dir)),
                'error': str(e)
            })
    
    return {
        'tool': 'complexity',
        'files_analyzed': len(complexity_results),
        'results': complexity_results,
        'summary': {
            'total_functions': sum(len(r.get('functions', [])) for r in complexity_results),
            'high_complexity_count': sum(len(r.get('high_complexity_functions', [])) 
                                        for r in complexity_results)
        }
    }

def main():
    code_dir = Path(__file__).parent.parent / 'code' / 'analysis'
    
    if not code_dir.exists():
        print(f"Error: {code_dir} does not exist")
        return
    
    print("="*80)
    print("STATIC CODE ANALYSIS")
    print("="*80)
    print(f"Analyzing: {code_dir}\n")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'code_directory': str(code_dir),
        'analyses': {}
    }
    
    # Run analyses
    results['analyses']['pylint'] = run_pylint(code_dir)
    results['analyses']['mypy'] = run_mypy(code_dir)
    results['analyses']['bandit'] = run_bandit(code_dir)
    results['analyses']['complexity'] = analyze_complexity(code_dir)
    
    # Save results
    output_dir = Path(__file__).parent.parent / 'docs' / 'audit'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'static_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate human-readable report
    with open(output_dir / 'static_analysis_report.txt', 'w') as f:
        f.write("="*80 + "\n")
        f.write("STATIC CODE ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Timestamp: {results['timestamp']}\n")
        f.write(f"Code directory: {results['code_directory']}\n\n")
        
        for tool, analysis in results['analyses'].items():
            f.write(f"{tool.upper()}\n")
            f.write("-"*80 + "\n")
            
            if 'error' in analysis:
                f.write(f"Error: {analysis['error']}\n")
                if 'install' in analysis:
                    f.write(f"Install: {analysis['install']}\n")
            elif tool == 'complexity':
                f.write(f"Files analyzed: {analysis['files_analyzed']}\n")
                f.write(f"Total functions: {analysis['summary']['total_functions']}\n")
                f.write(f"High complexity functions (>10): {analysis['summary']['high_complexity_count']}\n\n")
                f.write("High complexity functions:\n")
                for file_result in analysis['results']:
                    if file_result.get('high_complexity_functions'):
                        f.write(f"  {file_result['file']}:\n")
                        for func in file_result['high_complexity_functions']:
                            f.write(f"    {func['name']} (line {func['line']}): complexity {func['complexity']}\n")
            else:
                if 'summary' in analysis:
                    for key, value in analysis['summary'].items():
                        f.write(f"{key}: {value}\n")
                f.write("\n")
    
    print(f"\n✅ Results saved to {output_dir}/")
    print(f"   - static_analysis.json")
    print(f"   - static_analysis_report.txt")

if __name__ == '__main__':
    main()

