# Complete Usage Guide - Multi-Agent Code Analyzer

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Advanced Usage](#advanced-usage)
3. [CLI Options](#cli-options)
4. [LangGraph Integration](#langgraph-integration)
5. [Configuration](#configuration)
6. [Examples](#examples)

## Basic Usage

### Analyze a Single File

```python
from code_analyzer_system import analyze_code_file

# Analyze a Python file
result = analyze_code_file("my_script.py")

# Print the full report
print(result["final_report"])

# Access specific data
issues = result["analysis_results"].issues
metrics = result["analysis_results"].metrics

print(f"Found {len(issues)} issues")
print(f"Lines of code: {metrics['lines_of_code']}")
```

### Analyze Code String

```python
from code_analyzer_system import analyze_code_string

code = """
def calculate(x, y):
    return eval(f"{x} + {y}")  # Security issue!
"""

result = analyze_code_string(code, "example.py")

# Get critical issues only
from code_analyzer_system import IssueSeverity

critical = [
    i for i in result["analysis_results"].issues 
    if i.severity == IssueSeverity.CRITICAL
]

for issue in critical:
    print(f"Line {issue.line_number}: {issue.description}")
```

## Advanced Usage

### Custom Workflow

```python
from code_analyzer_system import (
    CodeAnalyzerWorkflow,
    CodeParserAgent,
    SecurityAnalyzerAgent,
    ReportGeneratorAgent
)

# Create a security-focused workflow
class SecurityWorkflow(CodeAnalyzerWorkflow):
    def __init__(self):
        super().__init__()
        # Only use security-related agents
        self.agents = {
            "parser": CodeParserAgent(),
            "security": SecurityAnalyzerAgent(),
            "reporter": ReportGeneratorAgent(),
        }

# Use the custom workflow
workflow = SecurityWorkflow()
result = workflow.run(code, "secure.py")
```

### Filter Issues by Type

```python
from code_analyzer_system import analyze_code_file, IssueType

result = analyze_code_file("script.py")

# Get only security issues
security_issues = [
    i for i in result["analysis_results"].issues
    if i.issue_type == IssueType.SECURITY
]

# Get only performance issues
performance_issues = [
    i for i in result["analysis_results"].issues
    if i.issue_type == IssueType.PERFORMANCE
]

print(f"Security issues: {len(security_issues)}")
print(f"Performance issues: {len(performance_issues)}")
```

### Batch Analysis

```python
from pathlib import Path
from code_analyzer_system import analyze_code_file

def analyze_directory(directory, recursive=True):
    """Analyze all Python files in a directory"""
    path = Path(directory)
    
    if recursive:
        files = path.rglob("*.py")
    else:
        files = path.glob("*.py")
    
    results = []
    for file in files:
        print(f"Analyzing: {file}")
        try:
            result = analyze_code_file(str(file))
            results.append({
                "file": str(file),
                "issues": len(result["analysis_results"].issues),
                "result": result
            })
        except Exception as e:
            print(f"Error: {e}")
    
    return results

# Analyze a project
results = analyze_directory("src/", recursive=True)

# Print summary
total_issues = sum(r["issues"] for r in results)
print(f"\nTotal files: {len(results)}")
print(f"Total issues: {total_issues}")
```

## CLI Options

### Basic Commands

```bash
# Analyze single file
python cli.py script.py

# Analyze with JSON output
python cli.py script.py --format json

# Analyze with HTML output
python cli.py script.py --format html --output report.html
```

### Advanced Commands

```bash
# Show only critical and high severity
python cli.py script.py --severity critical,high

# Analyze directory recursively
python cli.py src/ --recursive

# Skip metrics and optimizations
python cli.py script.py --no-metrics --no-optimizations

# Statistics only
python cli.py script.py --stats-only

# Save to file
python cli.py script.py --output analysis.txt
```

### CI/CD Integration

```bash
#!/bin/bash
# ci-check.sh - Run in CI pipeline

python cli.py src/ --recursive --format json --output results.json

# Check for critical issues
CRITICAL=$(jq '.summary.total_issues' results.json)

if [ $CRITICAL -gt 0 ]; then
    echo "❌ Critical issues found!"
    exit 1
else
    echo "✅ No critical issues"
    exit 0
fi
```

## LangGraph Integration

### Basic LangGraph Setup

```python
# Install first: pip install langgraph langchain langchain-anthropic

from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from typing import TypedDict, Annotated
import operator

class CodeState(TypedDict):
    code: str
    issues: Annotated[list, operator.add]
    messages: Annotated[list, operator.add]

# Initialize LLM
llm = ChatAnthropic(model="claude-sonnet-4-20250514")

# Define agent functions
def analyze_security(state: CodeState) -> CodeState:
    prompt = f"Analyze for security issues: {state['code']}"
    response = llm.invoke(prompt)
    state['messages'].append(response.content)
    return state

# Build workflow
workflow = StateGraph(CodeState)
workflow.add_node("security", analyze_security)
workflow.add_edge("security", END)
workflow.set_entry_point("security")

# Compile and run
app = workflow.compile()
result = app.invoke({"code": code, "issues": [], "messages": []})
```

### Conditional Routing

```python
from typing import Literal

def route_based_on_issues(state: CodeState) -> Literal["fixer", "reporter"]:
    """Route to auto-fixer if issues are simple"""
    if len(state["issues"]) < 5:
        return "fixer"
    return "reporter"

workflow.add_conditional_edges(
    "analyzer",
    route_based_on_issues,
    {
        "fixer": "auto_fixer",
        "reporter": "report_generator"
    }
)
```

### Human-in-the-Loop

```python
def should_ask_human(state: CodeState) -> str:
    """Ask human for complex issues"""
    critical_count = len([i for i in state["issues"] if i["severity"] == "critical"])
    
    if critical_count > 3:
        return "human_review"
    return "continue"

workflow.add_conditional_edges(
    "analyzer",
    should_ask_human,
    {
        "human_review": "wait_for_human",
        "continue": "report_generator"
    }
)
```

## Configuration

### Using Predefined Configs

```python
from config import load_config, STRICT_CONFIG
from code_analyzer_system import CodeAnalyzerWorkflow

# Load strict configuration
config = load_config("strict")

# Or use directly
config = STRICT_CONFIG

# Apply to workflow (requires custom implementation)
workflow = CodeAnalyzerWorkflow()
# Configure based on config settings
```

### Custom Configuration

```python
from config import AnalyzerConfig

custom_config = AnalyzerConfig(
    enabled_agents={"parser", "security"},
    min_severity="high",
    max_cyclomatic_complexity=5,
    check_hardcoded_secrets=True,
    ignore_patterns=[
        "*/test_*",
        "*/migrations/*"
    ]
)
```

## Examples

### Example 1: Security Audit

```python
from code_analyzer_system import analyze_code_file, IssueType, IssueSeverity

def security_audit(file_path):
    """Perform security audit on a file"""
    result = analyze_code_file(file_path)
    
    security_issues = [
        i for i in result["analysis_results"].issues
        if i.issue_type == IssueType.SECURITY
    ]
    
    critical_security = [
        i for i in security_issues
        if i.severity == IssueSeverity.CRITICAL
    ]
    
    print(f"Security Audit: {file_path}")
    print(f"Total security issues: {len(security_issues)}")
    print(f"Critical security issues: {len(critical_security)}")
    
    for issue in critical_security:
        print(f"\n⚠️  Line {issue.line_number}")
        print(f"   {issue.description}")
        print(f"   Fix: {issue.suggestion}")
    
    return len(critical_security) == 0

# Run audit
is_secure = security_audit("app.py")
if not is_secure:
    print("\n❌ Security issues must be fixed!")
```

### Example 2: Performance Report

```python
from code_analyzer_system import analyze_code_file, IssueType

def performance_report(file_path):
    """Generate performance report"""
    result = analyze_code_file(file_path)
    
    perf_issues = [
        i for i in result["analysis_results"].issues
        if i.issue_type == IssueType.PERFORMANCE
    ]
    
    complexity_metrics = {
        k: v for k, v in result["analysis_results"].metrics.items()
        if k.startswith("complexity_")
    }
    
    print("Performance Report")
    print("=" * 50)
    print(f"Performance Issues: {len(perf_issues)}")
    print(f"Optimization Suggestions: {len(result['analysis_results'].optimizations)}")
    
    print("\nFunction Complexity:")
    for func, complexity in complexity_metrics.items():
        func_name = func.replace("complexity_", "")
        status = "⚠️" if complexity > 10 else "✓"
        print(f"  {status} {func_name}: {complexity}")
    
    print("\nOptimizations:")
    for opt in result["analysis_results"].optimizations:
        print(f"  • {opt}")

performance_report("algorithm.py")
```

### Example 3: Pre-commit Hook

```python
#!/usr/bin/env python3
"""Pre-commit hook to check code quality"""

import sys
from pathlib import Path
from code_analyzer_system import analyze_code_file, IssueSeverity

def check_staged_files():
    """Check all staged Python files"""
    # Get staged files (simplified)
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True
    )
    
    files = [f for f in result.stdout.split('\n') if f.endswith('.py')]
    
    has_errors = False
    
    for file in files:
        if not Path(file).exists():
            continue
        
        print(f"Checking: {file}")
        result = analyze_code_file(file)
        
        critical_issues = [
            i for i in result["analysis_results"].issues
            if i.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]
        ]
        
        if critical_issues:
            has_errors = True
            print(f"❌ {file}: {len(critical_issues)} critical/high issues")
            for issue in critical_issues:
                print(f"   Line {issue.line_number}: {issue.description}")
    
    if has_errors:
        print("\n❌ Commit blocked due to code issues")
        sys.exit(1)
    else:
        print("\n✅ All checks passed")
        sys.exit(0)

if __name__ == "__main__":
    check_staged_files()
```

### Example 4: Generate Quality Badge

```python
from code_analyzer_system import analyze_code_file

def get_quality_score(file_path):
    """Calculate code quality score (0-100)"""
    result = analyze_code_file(file_path)
    issues = result["analysis_results"].issues
    
    # Calculate penalty based on severity
    penalties = {
        "critical": 20,
        "high": 10,
        "medium": 5,
        "low": 2,
        "info": 1
    }
    
    total_penalty = sum(
        penalties.get(i.severity.value, 0) for i in issues
    )
    
    # Start with 100, subtract penalties
    score = max(0, 100 - total_penalty)
    
    return score

def get_grade(score):
    """Convert score to letter grade"""
    if score >= 90:
        return "A", "🟢"
    elif score >= 80:
        return "B", "🟡"
    elif score >= 70:
        return "C", "🟠"
    elif score >= 60:
        return "D", "🔴"
    else:
        return "F", "🔴"

# Calculate score
score = get_quality_score("script.py")
grade, emoji = get_grade(score)

print(f"Code Quality: {grade} {emoji}")
print(f"Score: {score}/100")
```

### Example 5: Team Dashboard

```python
from pathlib import Path
from code_analyzer_system import analyze_code_file
import json

def generate_team_dashboard(project_dir):
    """Generate team code quality dashboard"""
    files = list(Path(project_dir).rglob("*.py"))
    
    dashboard = {
        "total_files": len(files),
        "total_issues": 0,
        "issues_by_severity": {},
        "issues_by_type": {},
        "top_issues": []
    }
    
    for file in files:
        result = analyze_code_file(str(file))
        issues = result["analysis_results"].issues
        
        dashboard["total_issues"] += len(issues)
        
        for issue in issues:
            # Count by severity
            severity = issue.severity.value
            dashboard["issues_by_severity"][severity] = \
                dashboard["issues_by_severity"].get(severity, 0) + 1
            
            # Count by type
            itype = issue.issue_type.value
            dashboard["issues_by_type"][itype] = \
                dashboard["issues_by_type"].get(itype, 0) + 1
    
    # Save dashboard
    with open("dashboard.json", "w") as f:
        json.dump(dashboard, f, indent=2)
    
    print("Team Dashboard")
    print("=" * 50)
    print(f"Files analyzed: {dashboard['total_files']}")
    print(f"Total issues: {dashboard['total_issues']}")
    print("\nBy Severity:")
    for severity, count in dashboard["issues_by_severity"].items():
        print(f"  {severity}: {count}")

generate_team_dashboard("src/")
```

## Tips and Best Practices

1. **Start with critical issues**: Always fix security and syntax errors first
2. **Run regularly**: Integrate into your development workflow
3. **Customize for your team**: Adjust severity thresholds and rules
4. **Use in CI/CD**: Prevent issues from reaching production
5. **Track over time**: Monitor code quality trends
6. **Don't ignore low severity**: They can accumulate into technical debt
7. **Review reports**: Understand issues, don't just auto-fix
8. **Balance strictness**: Too strict can slow development, too permissive allows bugs

## Troubleshooting

### Issue: Too many false positives
**Solution**: Adjust configuration, add ignore patterns, or customize detection rules

### Issue: Analysis is slow
**Solution**: Use parallel processing for multiple files, or focus on changed files only

### Issue: Missing detection
**Solution**: Add custom patterns in configuration or extend agent detection logic

### Issue: Can't install LangGraph
**Solution**: Use the standalone `code_analyzer_system.py` which has no dependencies

---

For more information, see README.md