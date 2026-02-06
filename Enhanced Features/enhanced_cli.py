#!/usr/bin/env python3
"""
Enhanced CLI with GitHub Integration and Multi-Language Support
Usage: python enhanced_cli.py [file/directory/github-url]
"""

import argparse
import sys
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Code Analyzer - Enhanced with GitHub & Multi-Language Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a Python file
  python enhanced_cli.py script.py
  
  # Analyze GitHub repository
  python enhanced_cli.py https://github.com/username/repo
  
  # Analyze with specific branch
  python enhanced_cli.py https://github.com/username/repo --branch develop
  
  # Analyze directory with multiple languages
  python enhanced_cli.py src/ --recursive --languages python,javascript,java
  
  # JSON output for GitHub repo
  python enhanced_cli.py https://github.com/username/repo --format json --output report.json
  
  # Only show critical issues
  python enhanced_cli.py https://github.com/username/repo --severity critical,high
        """
    )
    
    parser.add_argument(
        'path',
        help='Path to file/directory OR GitHub repository URL'
    )
    
    parser.add_argument(
        '--branch',
        default='main',
        help='Git branch to analyze (for GitHub URLs, default: main)'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively analyze all files in directory'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file for report (default: stdout)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'html'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '-s', '--severity',
        help='Filter by severity (comma-separated: critical,high,medium,low,info)'
    )
    
    parser.add_argument(
        '--languages',
        help='Languages to analyze (comma-separated: python,javascript,java,sql)'
    )
    
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Show only summary statistics'
    )
    
    args = parser.parse_args()
    
    # Check if it's a GitHub URL
    if args.path.startswith('http') and 'github.com' in args.path:
        analyze_github(args)
    else:
        analyze_local(args)


def analyze_github(args):
    """Analyze GitHub repository"""
    try:
        from github_integration import analyze_github_repo
        
        print(f"\n🔗 Analyzing GitHub Repository: {args.path}")
        print(f"   Branch: {args.branch}")
        print(f"   Format: {args.format}")
        print("\n" + "=" * 80)
        
        # Analyze
        report = analyze_github_repo(args.path, args.branch, args.format)
        
        # Apply severity filter if needed
        if args.severity and args.format == 'json':
            report = filter_json_by_severity(report, args.severity)
        
        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n✅ Report saved to: {args.output}")
        else:
            print(report)
    
    except ImportError:
        print("\n❌ Error: GitHub integration requires additional setup")
        print("\nPlease ensure:")
        print("1. git is installed: sudo apt-get install git")
        print("2. Required files are present:")
        print("   - github_integration.py")
        print("   - multi_language_analyzer.py")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error analyzing GitHub repository: {e}")
        print("\nTips:")
        print("- Check if the repository URL is correct")
        print("- Try a different branch: --branch master")
        print("- Ensure you have internet connection")
        print("- Check if git is installed: git --version")
        sys.exit(1)


def analyze_local(args):
    """Analyze local files/directories"""
    path = Path(args.path)
    
    if not path.exists():
        print(f"❌ Error: Path '{args.path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Collect files
    files_to_analyze = []
    
    if path.is_file():
        files_to_analyze.append(path)
    elif path.is_dir():
        extensions = get_extensions_for_languages(args.languages)
        
        if args.recursive:
            for ext in extensions:
                files_to_analyze.extend(path.rglob(f'*{ext}'))
        else:
            for ext in extensions:
                files_to_analyze.extend(path.glob(f'*{ext}'))
        
        if not files_to_analyze:
            print(f"❌ Error: No supported code files found in '{path}'", file=sys.stderr)
            sys.exit(1)
    
    print(f"\n📁 Analyzing {len(files_to_analyze)} file(s)...")
    print("=" * 80 + "\n")
    
    # Analyze files
    all_results = []
    
    for file_path in files_to_analyze:
        print(f"Analyzing: {file_path}")
        try:
            result = analyze_file_by_extension(file_path)
            all_results.append(result)
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
    
    # Generate output
    if args.format == 'json':
        output = generate_json_output(all_results, args.severity)
    else:
        output = generate_text_output(all_results, args.severity, args.stats_only)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\n✅ Report saved to: {args.output}")
    else:
        print("\n" + output)


def get_extensions_for_languages(languages_str):
    """Get file extensions for specified languages"""
    if not languages_str:
        return ['.py', '.js', '.java', '.sql', '.ts', '.jsx', '.tsx']
    
    lang_map = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'sql': ['.sql']
    }
    
    languages = [l.strip().lower() for l in languages_str.split(',')]
    extensions = []
    
    for lang in languages:
        extensions.extend(lang_map.get(lang, []))
    
    return extensions or ['.py']


def analyze_file_by_extension(file_path: Path):
    """Analyze file based on extension"""
    ext = file_path.suffix.lower()
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    # Determine language
    lang_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.sql': 'sql'
    }
    
    language = lang_map.get(ext, 'unknown')
    
    # Analyze
    if language == 'python':
        from code_analyzer_system import analyze_code_file
        result = analyze_code_file(str(file_path))
        return {
            "file": str(file_path),
            "language": "python",
            "result": result
        }
    else:
        from multi_language_analyzer import analyze_code
        result = analyze_code(code, language, str(file_path))
        return {
            "file": str(file_path),
            "language": language,
            "result": result
        }


def generate_json_output(results, severity_filter=None):
    """Generate JSON output"""
    output = {
        "summary": {
            "files_analyzed": len(results),
            "by_language": {}
        },
        "files": []
    }
    
    for result in results:
        lang = result.get("language", "unknown")
        output["summary"]["by_language"][lang] = \
            output["summary"]["by_language"].get(lang, 0) + 1
        
        if lang == 'python':
            issues = [
                {
                    "type": i.issue_type.value,
                    "severity": i.severity.value,
                    "line": i.line_number,
                    "description": i.description,
                    "suggestion": i.suggestion
                }
                for i in result["result"]["analysis_results"].issues
            ]
        else:
            issues = result["result"].get("issues", [])
        
        # Apply filter
        if severity_filter:
            severities = set(s.strip() for s in severity_filter.split(','))
            issues = [i for i in issues if i.get('severity') in severities]
        
        output["files"].append({
            "file": result["file"],
            "language": lang,
            "issues": issues
        })
    
    output["summary"]["total_issues"] = sum(
        len(f["issues"]) for f in output["files"]
    )
    
    return json.dumps(output, indent=2)


def generate_text_output(results, severity_filter=None, stats_only=False):
    """Generate text output"""
    lines = []
    
    lines.append("=" * 80)
    lines.append("MULTI-LANGUAGE CODE ANALYSIS REPORT")
    lines.append("=" * 80)
    
    # Summary
    total_issues = 0
    by_language = {}
    by_severity = {}
    
    for result in results:
        lang = result.get("language", "unknown")
        by_language[lang] = by_language.get(lang, 0) + 1
        
        if lang == 'python':
            issues = result["result"]["analysis_results"].issues
            for issue in issues:
                severity = issue.severity.value
                by_severity[severity] = by_severity.get(severity, 0) + 1
                total_issues += 1
        else:
            issues = result["result"].get("issues", [])
            for issue in issues:
                severity = issue.get('severity', 'unknown')
                by_severity[severity] = by_severity.get(severity, 0) + 1
                total_issues += 1
    
    lines.append(f"\nFiles Analyzed: {len(results)}")
    lines.append(f"Total Issues: {total_issues}")
    
    lines.append("\nBy Language:")
    for lang, count in sorted(by_language.items()):
        lines.append(f"  - {lang.title()}: {count}")
    
    lines.append("\nBy Severity:")
    for sev in ['critical', 'high', 'medium', 'low', 'info']:
        count = by_severity.get(sev, 0)
        if count > 0:
            lines.append(f"  - {sev.upper()}: {count}")
    
    if not stats_only:
        lines.append("\n" + "=" * 80)
        lines.append("DETAILED RESULTS")
        lines.append("=" * 80)
        
        for result in results[:10]:  # Show top 10
            lines.append(f"\n📄 {result['file']}")
            lines.append(f"   Language: {result['language']}")
            
            if result['language'] == 'python':
                issues = result["result"]["analysis_results"].issues
                lines.append(f"   Issues: {len(issues)}")
            else:
                issues = result["result"].get("issues", [])
                lines.append(f"   Issues: {len(issues)}")
    
    return "\n".join(lines)


def filter_json_by_severity(json_str, severity_filter):
    """Filter JSON report by severity"""
    data = json.loads(json_str)
    severities = set(s.strip() for s in severity_filter.split(','))
    
    for file_data in data.get('files', []):
        issues = file_data.get('issues', [])
        file_data['issues'] = [
            i for i in issues if i.get('severity') in severities
        ]
    
    return json.dumps(data, indent=2)


if __name__ == "__main__":
    main()