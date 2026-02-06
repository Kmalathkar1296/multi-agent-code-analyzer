#!/usr/bin/env python3
"""
Quick Start Demo - Multi-Agent Code Analyzer
Run this to see the system in action
"""

import sys
from code_analyzer_system import analyze_code_string, IssueSeverity, IssueType


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def demo_basic_analysis():
    """Demo 1: Basic code analysis"""
    print_header("DEMO 1: Basic Code Analysis")
    
    code = '''
def calculate_sum(numbers=[]):  # Mutable default argument
    total = 0
    for i in range(len(numbers)):  # Inefficient
        total += numbers[i]
    return total

password = "secret123"  # Hardcoded password

def unsafe_query(user_input):
    return eval(user_input)  # Security risk!
'''
    
    result = analyze_code_string(code, "demo1.py")
    
    # Show summary
    issues = result["analysis_results"].issues
    print(f"Total issues found: {len(issues)}")
    
    # Group by severity
    by_severity = {}
    for issue in issues:
        severity = issue.severity.value
        by_severity[severity] = by_severity.get(severity, 0) + 1
    
    print("\nIssues by severity:")
    for severity in ["critical", "high", "medium", "low", "info"]:
        count = by_severity.get(severity, 0)
        if count > 0:
            print(f"  {severity.upper()}: {count}")
    
    # Show critical issues
    critical = [i for i in issues if i.severity == IssueSeverity.CRITICAL]
    if critical:
        print(f"\n⚠️  Critical Issues ({len(critical)}):")
        for issue in critical:
            print(f"  • Line {issue.line_number}: {issue.description}")
            print(f"    Fix: {issue.suggestion}")


def demo_security_focus():
    """Demo 2: Security-focused analysis"""
    print_header("DEMO 2: Security Analysis")
    
    code = '''
import random

API_KEY = "sk-1234567890abcdef"  # Exposed secret
DB_PASSWORD = "admin123"

def authenticate(username, password):
    query = "SELECT * FROM users WHERE user='%s' AND pass='%s'" % (username, password)
    # SQL injection vulnerability
    return query

def process_input(user_data):
    result = eval(user_data)  # Code injection
    return result

def generate_session_token():
    return ''.join(random.choices('0123456789abcdef', k=32))  # Insecure random
'''
    
    result = analyze_code_string(code, "demo2.py")
    
    # Get security issues only
    security_issues = [
        i for i in result["analysis_results"].issues
        if i.issue_type == IssueType.SECURITY
    ]
    
    print(f"Security issues found: {len(security_issues)}")
    
    for idx, issue in enumerate(security_issues, 1):
        print(f"\n{idx}. {issue.description}")
        print(f"   Line: {issue.line_number}")
        print(f"   Severity: {issue.severity.value.upper()}")
        if issue.suggestion:
            print(f"   💡 {issue.suggestion}")


def demo_performance_analysis():
    """Demo 3: Performance analysis"""
    print_header("DEMO 3: Performance Analysis")
    
    code = '''
def process_data(items):
    result = ""
    for item in items:
        result = result + str(item) + ","  # Slow string concatenation
    return result

def get_even_numbers(numbers):
    result = []
    for i in range(len(numbers)):  # Should use enumerate
        if numbers[i] % 2 == 0:
            result.append(numbers[i])  # Could use list comprehension
    return result

def complex_function(a, b, c, d, e, f):
    # High complexity
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            return a + b + c + d + e + f
    return 0
'''
    
    result = analyze_code_string(code, "demo3.py")
    
    # Performance issues
    perf_issues = [
        i for i in result["analysis_results"].issues
        if i.issue_type == IssueType.PERFORMANCE
    ]
    
    print(f"Performance issues: {len(perf_issues)}")
    for issue in perf_issues:
        print(f"\n• Line {issue.line_number}: {issue.description}")
        if issue.suggestion:
            print(f"  Fix: {issue.suggestion}")
    
    # Optimizations
    optimizations = result["analysis_results"].optimizations
    if optimizations:
        print(f"\nOptimization suggestions ({len(optimizations)}):")
        for opt in optimizations:
            print(f"  • {opt}")
    
    # Complexity
    metrics = result["analysis_results"].metrics
    print("\nFunction complexity:")
    for key, value in metrics.items():
        if key.startswith("complexity_"):
            func_name = key.replace("complexity_", "")
            status = "⚠️" if value > 10 else "✓"
            print(f"  {status} {func_name}: {value}")


def demo_complete_report():
    """Demo 4: Complete analysis with report"""
    print_header("DEMO 4: Complete Analysis Report")
    
    code = '''
import random

class UserManager:
    def validate_user(self, username, password):
        query = "SELECT * FROM users WHERE name='%s'" % username
        # Multiple issues here
        return query
    
    def create_token(self):
        return random.randint(1000, 9999)  # Insecure
'''
    
    result = analyze_code_string(code, "demo4.py")
    
    # Show abbreviated report
    issues = result["analysis_results"].issues
    metrics = result["analysis_results"].metrics
    
    print(f"File: demo4.py")
    print(f"Lines of code: {metrics.get('lines_of_code', 'N/A')}")
    print(f"Functions: {metrics.get('num_functions', 'N/A')}")
    print(f"Classes: {metrics.get('num_classes', 'N/A')}")
    print(f"\nTotal issues: {len(issues)}")
    
    # Group by type
    by_type = {}
    for issue in issues:
        itype = issue.issue_type.value
        by_type[itype] = by_type.get(itype, 0) + 1
    
    print("\nIssues by type:")
    for itype, count in sorted(by_type.items()):
        print(f"  {itype.replace('_', ' ').title()}: {count}")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "   MULTI-AGENT CODE ANALYZER - QUICK START DEMO".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    demos = [
        ("Basic Analysis", demo_basic_analysis),
        ("Security Focus", demo_security_focus),
        ("Performance Analysis", demo_performance_analysis),
        ("Complete Report", demo_complete_report),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"Error in {name}: {e}")
            import traceback
            traceback.print_exc()
        
        if demo_func != demos[-1][1]:  # Not last demo
            print("\n" + "-" * 80)
            input("Press Enter to continue to next demo...")
    
    print_header("ALL DEMOS COMPLETED!")
    print("✅ You've seen the multi-agent system in action!")
    print("\nNext steps:")
    print("  1. Try analyzing your own code: python cli.py your_script.py")
    print("  2. Read the USAGE_GUIDE.md for more examples")
    print("  3. Check README.md for full documentation")
    print("  4. Customize the system for your needs")
    print("\nHappy coding! 🚀\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)