#!/usr/bin/env python3
"""
Audit dependencies for:
- Outdated packages
- Security vulnerabilities
- License compatibility
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
import re

def get_installed_packages():
    """Get list of installed packages with versions."""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return []
    except Exception as e:
        return {'error': str(e)}

def check_outdated_packages():
    """Check for outdated packages."""
    print("Checking for outdated packages...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            outdated = json.loads(result.stdout)
        else:
            outdated = []
        
        return {
            'outdated_count': len(outdated),
            'packages': outdated
        }
    except Exception as e:
        return {'error': str(e)}

def check_security_vulnerabilities():
    """Check for known security vulnerabilities using safety."""
    print("Checking for security vulnerabilities...")
    
    try:
        result = subprocess.run(
            ['safety', 'check', '--json'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            vulnerabilities = []
        else:
            try:
                vulnerabilities = json.loads(result.stdout)
            except:
                vulnerabilities = [{'raw': result.stdout}]
        
        return {
            'vulnerability_count': len(vulnerabilities),
            'vulnerabilities': vulnerabilities
        }
    except FileNotFoundError:
        return {
            'error': 'safety not installed',
            'install': 'pip install safety'
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_requirements_file(requirements_path: Path):
    """Analyze requirements.txt file."""
    if not requirements_path.exists():
        return {'error': 'File not found'}
    
    requirements = []
    with open(requirements_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse requirement
                match = re.match(r'([a-zA-Z0-9_-]+)([><=!]+)?([0-9.]+)?', line)
                if match:
                    requirements.append({
                        'package': match.group(1),
                        'operator': match.group(2) or '>=',
                        'version': match.group(3) or 'latest',
                        'raw': line
                    })
    
    return {
        'file': str(requirements_path),
        'requirements': requirements,
        'count': len(requirements)
    }

def check_license_compatibility():
    """Check license compatibility (basic check)."""
    print("Checking license compatibility...")
    
    # Common licenses and compatibility
    licenses = {
        'MIT': 'permissive',
        'Apache-2.0': 'permissive',
        'BSD': 'permissive',
        'GPL-2.0': 'copyleft',
        'GPL-3.0': 'copyleft',
        'LGPL': 'lesser-copyleft',
        'AGPL': 'strong-copyleft'
    }
    
    # This is a simplified check - real license checking requires
    # querying package metadata or PyPI
    return {
        'note': 'Full license checking requires package metadata',
        'common_licenses': licenses
    }

def main():
    print("="*80)
    print("DEPENDENCY AUDIT")
    print("="*80)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'audits': {}
    }
    
    # Get installed packages
    print("\n1. Getting installed packages...")
    installed = get_installed_packages()
    results['audits']['installed_packages'] = {
        'count': len(installed) if isinstance(installed, list) else 0,
        'packages': installed[:20] if isinstance(installed, list) else installed  # First 20
    }
    
    # Check outdated
    print("\n2. Checking for outdated packages...")
    results['audits']['outdated'] = check_outdated_packages()
    
    # Check security
    print("\n3. Checking for security vulnerabilities...")
    results['audits']['security'] = check_security_vulnerabilities()
    
    # Analyze requirements files
    print("\n4. Analyzing requirements files...")
    repo_root = Path(__file__).parent.parent
    requirements_files = list(repo_root.rglob('requirements.txt'))
    
    requirements_analysis = []
    for req_file in requirements_files:
        analysis = analyze_requirements_file(req_file)
        requirements_analysis.append(analysis)
    
    results['audits']['requirements_files'] = requirements_analysis
    
    # License check
    print("\n5. License compatibility check...")
    results['audits']['licenses'] = check_license_compatibility()
    
    # Save results
    output_dir = Path(__file__).parent.parent / 'docs' / 'audit'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'dependency_audit.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    with open(output_dir / 'dependency_audit_report.txt', 'w') as f:
        f.write("="*80 + "\n")
        f.write("DEPENDENCY AUDIT REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Timestamp: {results['timestamp']}\n\n")
        
        f.write("INSTALLED PACKAGES\n")
        f.write("-"*80 + "\n")
        f.write(f"Total: {results['audits']['installed_packages']['count']}\n\n")
        
        f.write("OUTDATED PACKAGES\n")
        f.write("-"*80 + "\n")
        if 'error' in results['audits']['outdated']:
            f.write(f"Error: {results['audits']['outdated']['error']}\n")
        else:
            f.write(f"Count: {results['audits']['outdated']['outdated_count']}\n")
            for pkg in results['audits']['outdated'].get('packages', [])[:10]:
                f.write(f"  {pkg.get('name', 'unknown')}: {pkg.get('version', '?')} -> {pkg.get('latest_version', '?')}\n")
        f.write("\n")
        
        f.write("SECURITY VULNERABILITIES\n")
        f.write("-"*80 + "\n")
        if 'error' in results['audits']['security']:
            f.write(f"Error: {results['audits']['security']['error']}\n")
            if 'install' in results['audits']['security']:
                f.write(f"Install: {results['audits']['security']['install']}\n")
        else:
            f.write(f"Count: {results['audits']['security']['vulnerability_count']}\n")
        f.write("\n")
        
        f.write("REQUIREMENTS FILES\n")
        f.write("-"*80 + "\n")
        for req_analysis in results['audits']['requirements_files']:
            if 'error' not in req_analysis:
                f.write(f"{req_analysis['file']}: {req_analysis['count']} packages\n")
        f.write("\n")
        
        f.write("LICENSE COMPATIBILITY\n")
        f.write("-"*80 + "\n")
        f.write("Note: Full license checking requires package metadata\n")
        f.write("Common license types:\n")
        for license, type in results['audits']['licenses'].get('common_licenses', {}).items():
            f.write(f"  {license}: {type}\n")
    
    print(f"\n✅ Results saved to {output_dir}/")
    print(f"   - dependency_audit.json")
    print(f"   - dependency_audit_report.txt")

if __name__ == '__main__':
    main()

