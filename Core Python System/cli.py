#!/usr/bin/env python3
"""
CLI Interface for Multi-Agent Code Analyzer
Usage: python cli.py <file_path>
"""

import argparse
import sys
import json
from pathlib import Path
from code_analyzer_system import (
    analyze_code_file,
    analyze_code_string,
    CodeAnalyzerWorkflow
)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Code Analyzer - Automated Python code analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single file
  python cli.py script.py
  
  # Analyze with JSON output
  python cli.py script.py --format json
  
  # Analyze directory
  python cli.py src/ --recursive
  
  # Only show critical and high severity issues
  python cli.py script.py --severity critical,high
  
  # Save report to file
  python cli.py script.py --output report.txt
        """
    )
    
    parser.add_argument(
        'path',
        help='Path to Python file or directory to analyze'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively analyze all Python files in directory'
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
        help='Comma-separated list of severities to show (critical,high,medium,low,info)'
    )
    
    parser.add_argument(
        '--no-metrics',
        action='store_true',
        help='Skip code metrics in output'
    )
    
    parser.add_argument(
        '--no-optimizations',
        action='store_true',
        help='Skip optimization suggestions'
    )
    
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Show only summary statistics'
    )
    
    args = parser.parse_args()
    
    # Validate path
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path '{args.path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Collect files to analyze
    files_to_analyze = []
    
    if path.is_file():
        if path.suffix != '.py':
            print(f"Warning: '{path}' is not a Python file", file=sys.stderr)
        files_to_analyze.append(path)
    elif path.is_dir():
        if args.recursive:
            files_to_analyze = list(path.rglob('*.py'))
        else:
            files_to_analyze = list(path.glob('*.py'))
        
        if not files_to_analyze:
            print(f"Error: No Python files found in '{path}'", file=sys.stderr)
            sys.exit(1)
    
    # Parse severity filter
    severity_filter = None
    if args.severity:
        severity_filter = set(s.strip().lower() for s in args.severity.split(','))
    
    # Analyze files
    all_results = []
    
    print(f"\n{'='*80}")
    print(f"Analyzing {len(files_to_analyze)} file(s)...")
    print(f"{'='*80}\n")
    
    for file_path in files_to_analyze:
        print(f"Analyzing: {file_path}")
        try:
            result = analyze_code_file(str(file_path))
            all_results.append(result)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}", file=sys.stderr)
    
    # Generate output
    if args.format == 'json':
        output = generate_json_output(all_results, severity_filter)
    elif args.format == 'html':
        output = generate_html_output(all_results, severity_filter)
    else:
        output = generate_text_output(
            all_results,
            severity_filter,
            args.stats_only,
            args.no_metrics,
            args.no_optimizations
        )
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\nReport saved to: {args.output}")
    else:
        print(output)


def generate_json_output(results, severity_filter=None):
    """Generate JSON output"""
    output = {
        "summary": {
            "files_analyzed": len(results),
            "total_issues": sum(len(r["analysis_results"].issues) for r in results),
            "total_optimizations": sum(len(r["analysis_results"].optimizations) for r in results),
        },
        "files": []
    }
    
    for result in results:
        issues = result["analysis_results"].issues
        
        if severity_filter:
            issues = [i for i in issues if i.severity.value in severity_filter]
        
        file_data = {
            "path": result["file_path"],
            "metrics": result["analysis_results"].metrics,
            "issues": [
                {
                    "type": i.issue_type.value,
                    "severity": i.severity.value,
                    "line": i.line_number,
                    "description": i.description,
                    "suggestion": i.suggestion
                }
                for i in issues
            ],
            "optimizations": result["analysis_results"].optimizations
        }
        
        output["files"].append(file_data)
    
    return json.dumps(output, indent=2)


def generate_html_output(results, severity_filter=None):
    """Generate HTML output"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Code Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; }
        h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        .summary { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .file { border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 5px; }
        .issue { margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }
        .critical { border-left-color: #dc3545; background: #f8d7da; }
        .high { border-left-color: #fd7e14; background: #fff3cd; }
        .medium { border-left-color: #ffc107; background: #fff3cd; }
        .low { border-left-color: #28a745; background: #d4edda; }
        .info { border-left-color: #17a2b8; background: #d1ecf1; }
        .code { background: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .metric { background: #f8f9fa; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Code Analysis Report</h1>
"""
    
    # Summary
    total_issues = sum(len(r["analysis_results"].issues) for r in results)
    html += f"""
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Files Analyzed:</strong> {len(results)}</p>
            <p><strong>Total Issues Found:</strong> {total_issues}</p>
        </div>
"""
    
    # Files
    for result in results:
        issues = result["analysis_results"].issues
        if severity_filter:
            issues = [i for i in issues if i.severity.value in severity_filter]
        
        html += f"""
        <div class="file">
            <h2>📄 {result["file_path"]}</h2>
            <div class="metrics">
                <div class="metric">Lines: {result["analysis_results"].metrics.get('lines_of_code', 'N/A')}</div>
                <div class="metric">Functions: {result["analysis_results"].metrics.get('num_functions', 'N/A')}</div>
                <div class="metric">Classes: {result["analysis_results"].metrics.get('num_classes', 'N/A')}</div>
                <div class="metric">Issues: {len(issues)}</div>
            </div>
            <h3>Issues</h3>
"""
        
        if not issues:
            html += "<p>✅ No issues found!</p>"
        else:
            for issue in issues:
                html += f"""
            <div class="issue {issue.severity.value}">
                <strong>{issue.issue_type.value.replace('_', ' ').title()}</strong> 
                ({issue.severity.value.upper()}) - Line {issue.line_number}
                <p>{issue.description}</p>
                {f'<div class="code">{issue.code_snippet}</div>' if issue.code_snippet else ''}
                {f'<p><strong>💡 Suggestion:</strong> {issue.suggestion}</p>' if issue.suggestion else ''}
            </div>
"""
        
        html += """
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    return html


def generate_text_output(results, severity_filter=None, stats_only=False, 
                        no_metrics=False, no_optimizations=False):
    """Generate text output"""
    if stats_only:
        output = []
        output.append("\n" + "="*80)
        output.append("ANALYSIS STATISTICS")
        output.append("="*80)
        
        for result in results:
            issues = result["analysis_results"].issues
            if severity_filter:
                issues = [i for i in issues if i.severity.value in severity_filter]
            
            output.append(f"\nFile: {result['file_path']}")
            output.append(f"  Issues: {len(issues)}")
            output.append(f"  Optimizations: {len(result['analysis_results'].optimizations)}")
        
        return "\n".join(output)
    
    output = []
    
    for result in results:
        report = result["final_report"]
        
        if severity_filter or no_metrics or no_optimizations:
            # Filter report
            lines = report.split('\n')
            filtered_lines = []
            skip_section = False
            
            for line in lines:
                if no_metrics and 'METRICS' in line:
                    skip_section = True
                elif no_optimizations and 'OPTIMIZATION' in line:
                    skip_section = True
                elif line.startswith('='):
                    skip_section = False
                
                if not skip_section:
                    filtered_lines.append(line)
            
            report = '\n'.join(filtered_lines)
        
        output.append(report)
    
    return "\n\n".join(output)


if __name__ == "__main__":
    main()