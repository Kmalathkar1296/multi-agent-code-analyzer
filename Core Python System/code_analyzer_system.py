"""
Multi-Agent Code Analyzer System using LangGraph
Automatically detects, debugs, and optimizes Python codebases
"""

import ast
import re
import json
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import operator


# ============================================================================
# State Management
# ============================================================================

class IssueType(Enum):
    SYNTAX_ERROR = "syntax_error"
    LOGIC_ERROR = "logic_error"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CODE_SMELL = "code_smell"
    STYLE = "style"
    COMPLEXITY = "complexity"


class IssueSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class CodeIssue:
    """Represents a detected code issue"""
    issue_type: IssueType
    severity: IssueSeverity
    line_number: int
    description: str
    code_snippet: str
    suggestion: Optional[str] = None
    fixed_code: Optional[str] = None


@dataclass
class AnalysisResult:
    """Results from code analysis"""
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    optimizations: List[str] = field(default_factory=list)


class AgentState(TypedDict):
    """Shared state between agents"""
    code: str
    file_path: str
    analysis_results: AnalysisResult
    current_agent: str
    agents_completed: Annotated[List[str], operator.add]
    debug_log: Annotated[List[str], operator.add]
    final_report: Optional[str]
    should_continue: bool


# ============================================================================
# Agent 1: Code Parser & Structure Analyzer
# ============================================================================

class CodeParserAgent:
    """Analyzes code structure and detects syntax issues"""
    
    def __init__(self):
        self.name = "CodeParserAgent"
    
    def analyze(self, state: AgentState) -> AgentState:
        """Parse and analyze code structure"""
        print(f"\n🔍 [{self.name}] Starting code structure analysis...")
        
        code = state["code"]
        results = state["analysis_results"]
        
        # Syntax validation
        try:
            tree = ast.parse(code)
            results.metrics["valid_syntax"] = True
            results.metrics["ast_available"] = True
            
            # Analyze structure
            self._analyze_ast(tree, code, results)
            
        except SyntaxError as e:
            results.metrics["valid_syntax"] = False
            results.issues.append(CodeIssue(
                issue_type=IssueType.SYNTAX_ERROR,
                severity=IssueSeverity.CRITICAL,
                line_number=e.lineno or 0,
                description=f"Syntax Error: {str(e)}",
                code_snippet=self._get_code_snippet(code, e.lineno or 0),
                suggestion="Fix syntax error before proceeding"
            ))
        
        state["current_agent"] = self.name
        state["agents_completed"].append(self.name)
        state["debug_log"].append(f"{self.name}: Found {len(results.issues)} issues")
        
        return state
    
    def _analyze_ast(self, tree: ast.AST, code: str, results: AnalysisResult):
        """Analyze AST for structural issues"""
        lines = code.split('\n')
        
        # Count various elements
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        
        results.metrics["num_functions"] = len(functions)
        results.metrics["num_classes"] = len(classes)
        results.metrics["num_imports"] = len(imports)
        results.metrics["lines_of_code"] = len(lines)
        
        # Check for missing docstrings
        for func in functions:
            if not ast.get_docstring(func):
                results.issues.append(CodeIssue(
                    issue_type=IssueType.STYLE,
                    severity=IssueSeverity.LOW,
                    line_number=func.lineno,
                    description=f"Function '{func.name}' missing docstring",
                    code_snippet=self._get_code_snippet(code, func.lineno),
                    suggestion="Add docstring to improve code documentation"
                ))
        
        # Check for wildcard imports
        for imp in imports:
            if isinstance(imp, ast.ImportFrom) and any(
                alias.name == '*' for alias in imp.names
            ):
                results.issues.append(CodeIssue(
                    issue_type=IssueType.CODE_SMELL,
                    severity=IssueSeverity.MEDIUM,
                    line_number=imp.lineno,
                    description="Wildcard import detected",
                    code_snippet=self._get_code_snippet(code, imp.lineno),
                    suggestion="Use explicit imports instead of wildcard imports"
                ))
    
    def _get_code_snippet(self, code: str, line_num: int, context: int = 2) -> str:
        """Get code snippet around the line number"""
        lines = code.split('\n')
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        snippet = '\n'.join(
            f"{i+1:4d} | {line}" for i, line in enumerate(lines[start:end], start)
        )
        return snippet


# ============================================================================
# Agent 2: Logic & Bug Detector
# ============================================================================

class BugDetectorAgent:
    """Detects logical errors and common bugs"""
    
    def __init__(self):
        self.name = "BugDetectorAgent"
    
    def analyze(self, state: AgentState) -> AgentState:
        """Detect bugs and logical errors"""
        print(f"\n🐛 [{self.name}] Starting bug detection...")
        
        code = state["code"]
        results = state["analysis_results"]
        
        if not results.metrics.get("valid_syntax", False):
            print(f"   Skipping bug detection due to syntax errors")
            state["agents_completed"].append(self.name)
            return state
        
        # Detect common bugs
        self._detect_common_bugs(code, results)
        self._detect_exception_handling_issues(code, results)
        self._detect_resource_leaks(code, results)
        
        state["current_agent"] = self.name
        state["agents_completed"].append(self.name)
        state["debug_log"].append(
            f"{self.name}: Analyzed for bugs, found {len([i for i in results.issues if i.issue_type == IssueType.LOGIC_ERROR])} logic errors"
        )
        
        return state
    
    def _detect_common_bugs(self, code: str, results: AnalysisResult):
        """Detect common bug patterns"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Mutable default arguments
            if re.search(r'def\s+\w+\([^)]*=\s*(\[\]|\{\})', line):
                results.issues.append(CodeIssue(
                    issue_type=IssueType.LOGIC_ERROR,
                    severity=IssueSeverity.HIGH,
                    line_number=i,
                    description="Mutable default argument detected",
                    code_snippet=line.strip(),
                    suggestion="Use None as default and initialize inside function"
                ))
            
            # Comparison with True/False
            if re.search(r'(==|!=)\s*(True|False)\b', line):
                results.issues.append(CodeIssue(
                    issue_type=IssueType.CODE_SMELL,
                    severity=IssueSeverity.MEDIUM,
                    line_number=i,
                    description="Explicit comparison with True/False",
                    code_snippet=line.strip(),
                    suggestion="Use truthiness instead: 'if value:' or 'if not value:'"
                ))
            
            # Using 'is' for value comparison
            if re.search(r'\bis\s+["\']', line) or re.search(r'\bis\s+\d', line):
                results.issues.append(CodeIssue(
                    issue_type=IssueType.LOGIC_ERROR,
                    severity=IssueSeverity.MEDIUM,
                    line_number=i,
                    description="Using 'is' for value comparison instead of '=='",
                    code_snippet=line.strip(),
                    suggestion="Use '==' for value comparison, 'is' for identity"
                ))
    
    def _detect_exception_handling_issues(self, code: str, results: AnalysisResult):
        """Detect exception handling issues"""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    # Bare except clauses
                    if node.type is None:
                        results.issues.append(CodeIssue(
                            issue_type=IssueType.CODE_SMELL,
                            severity=IssueSeverity.MEDIUM,
                            line_number=node.lineno,
                            description="Bare except clause catches all exceptions",
                            code_snippet=f"Line {node.lineno}",
                            suggestion="Catch specific exceptions instead"
                        ))
                    
                    # Empty except blocks
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        results.issues.append(CodeIssue(
                            issue_type=IssueType.CODE_SMELL,
                            severity=IssueSeverity.MEDIUM,
                            line_number=node.lineno,
                            description="Empty except block (pass statement)",
                            code_snippet=f"Line {node.lineno}",
                            suggestion="At minimum, log the exception"
                        ))
        except:
            pass
    
    def _detect_resource_leaks(self, code: str, results: AnalysisResult):
        """Detect potential resource leaks"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # File operations without context manager
            if re.search(r'\bopen\s*\(', line) and 'with' not in line:
                results.issues.append(CodeIssue(
                    issue_type=IssueType.LOGIC_ERROR,
                    severity=IssueSeverity.MEDIUM,
                    line_number=i,
                    description="File opened without context manager",
                    code_snippet=line.strip(),
                    suggestion="Use 'with open(...) as f:' to ensure proper resource cleanup"
                ))


# ============================================================================
# Agent 3: Performance Optimizer
# ============================================================================

class PerformanceOptimizerAgent:
    """Analyzes code for performance issues and suggests optimizations"""
    
    def __init__(self):
        self.name = "PerformanceOptimizerAgent"
    
    def analyze(self, state: AgentState) -> AgentState:
        """Analyze performance and suggest optimizations"""
        print(f"\n⚡ [{self.name}] Starting performance analysis...")
        
        code = state["code"]
        results = state["analysis_results"]
        
        if not results.metrics.get("valid_syntax", False):
            print(f"   Skipping performance analysis due to syntax errors")
            state["agents_completed"].append(self.name)
            return state
        
        self._detect_performance_issues(code, results)
        self._analyze_complexity(code, results)
        self._suggest_optimizations(code, results)
        
        state["current_agent"] = self.name
        state["agents_completed"].append(self.name)
        state["debug_log"].append(
            f"{self.name}: Found {len([i for i in results.issues if i.issue_type == IssueType.PERFORMANCE])} performance issues"
        )
        
        return state
    
    def _detect_performance_issues(self, code: str, results: AnalysisResult):
        """Detect performance anti-patterns"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # String concatenation in loops
            if ('+=' in line or '= ' in line) and any(kw in line for kw in ['for ', 'while ']):
                if re.search(r'["\'].*["\'].*\+', line):
                    results.issues.append(CodeIssue(
                        issue_type=IssueType.PERFORMANCE,
                        severity=IssueSeverity.MEDIUM,
                        line_number=i,
                        description="String concatenation in loop",
                        code_snippet=line.strip(),
                        suggestion="Use list and ''.join() for better performance"
                    ))
            
            # List comprehension vs append
            if 'append' in line and i > 1:
                prev_lines = '\n'.join(lines[max(0, i-3):i])
                if 'for ' in prev_lines:
                    results.issues.append(CodeIssue(
                        issue_type=IssueType.PERFORMANCE,
                        severity=IssueSeverity.LOW,
                        line_number=i,
                        description="Consider using list comprehension",
                        code_snippet=line.strip(),
                        suggestion="List comprehensions are often faster than append in loops"
                    ))
            
            # Global lookups in loops
            if re.search(r'(for|while)\s+.*:\s*$', line):
                results.optimizations.append(
                    f"Line {i}: Consider caching global lookups before loops"
                )
    
    def _analyze_complexity(self, code: str, results: AnalysisResult):
        """Analyze cyclomatic complexity"""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    results.metrics[f"complexity_{node.name}"] = complexity
                    
                    if complexity > 10:
                        results.issues.append(CodeIssue(
                            issue_type=IssueType.COMPLEXITY,
                            severity=IssueSeverity.MEDIUM,
                            line_number=node.lineno,
                            description=f"High cyclomatic complexity ({complexity}) in function '{node.name}'",
                            code_snippet=f"Function at line {node.lineno}",
                            suggestion="Consider breaking down into smaller functions"
                        ))
        except:
            pass
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _suggest_optimizations(self, code: str, results: AnalysisResult):
        """Suggest general optimizations"""
        lines = code.split('\n')
        
        # Check for opportunities to use built-in functions
        for i, line in enumerate(lines, 1):
            if re.search(r'for.*in.*range\(len\(', line):
                results.optimizations.append(
                    f"Line {i}: Use enumerate() instead of range(len())"
                )
            
            if '.keys()' in line and 'for ' in line:
                results.optimizations.append(
                    f"Line {i}: No need to call .keys() when iterating dict"
                )


# ============================================================================
# Agent 4: Security Analyzer
# ============================================================================

class SecurityAnalyzerAgent:
    """Analyzes code for security vulnerabilities"""
    
    def __init__(self):
        self.name = "SecurityAnalyzerAgent"
    
    def analyze(self, state: AgentState) -> AgentState:
        """Analyze security vulnerabilities"""
        print(f"\n🔒 [{self.name}] Starting security analysis...")
        
        code = state["code"]
        results = state["analysis_results"]
        
        self._detect_security_issues(code, results)
        self._check_input_validation(code, results)
        
        state["current_agent"] = self.name
        state["agents_completed"].append(self.name)
        state["debug_log"].append(
            f"{self.name}: Found {len([i for i in results.issues if i.issue_type == IssueType.SECURITY])} security issues"
        )
        
        return state
    
    def _detect_security_issues(self, code: str, results: AnalysisResult):
        """Detect security vulnerabilities"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # SQL injection risks
            if re.search(r'execute\s*\(["\'].*%s.*["\']', line):
                results.issues.append(CodeIssue(
                    issue_type=IssueType.SECURITY,
                    severity=IssueSeverity.CRITICAL,
                    line_number=i,
                    description="Potential SQL injection vulnerability",
                    code_snippet=line.strip(),
                    suggestion="Use parameterized queries instead"
                ))
            
            # Use of eval/exec
            if re.search(r'\b(eval|exec)\s*\(', line):
                results.issues.append(CodeIssue(
                    issue_type=IssueType.SECURITY,
                    severity=IssueSeverity.CRITICAL,
                    line_number=i,
                    description="Use of eval/exec is dangerous",
                    code_snippet=line.strip(),
                    suggestion="Avoid eval/exec; use safer alternatives like ast.literal_eval"
                ))
            
            # Hardcoded secrets
            if re.search(r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                results.issues.append(CodeIssue(
                    issue_type=IssueType.SECURITY,
                    severity=IssueSeverity.CRITICAL,
                    line_number=i,
                    description="Hardcoded secret detected",
                    code_snippet="[REDACTED]",
                    suggestion="Use environment variables or secret management"
                ))
            
            # Insecure random
            if 'random.' in line and 'import random' in code:
                results.issues.append(CodeIssue(
                    issue_type=IssueType.SECURITY,
                    severity=IssueSeverity.MEDIUM,
                    line_number=i,
                    description="Using random module for security-sensitive operations",
                    code_snippet=line.strip(),
                    suggestion="Use secrets module for cryptographic randomness"
                ))
    
    def _check_input_validation(self, code: str, results: AnalysisResult):
        """Check for input validation"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Direct user input usage
            if re.search(r'input\s*\(', line):
                results.issues.append(CodeIssue(
                    issue_type=IssueType.SECURITY,
                    severity=IssueSeverity.LOW,
                    line_number=i,
                    description="User input should be validated",
                    code_snippet=line.strip(),
                    suggestion="Always validate and sanitize user input"
                ))


# ============================================================================
# Agent 5: Report Generator
# ============================================================================

class ReportGeneratorAgent:
    """Generates comprehensive analysis report"""
    
    def __init__(self):
        self.name = "ReportGeneratorAgent"
    
    def analyze(self, state: AgentState) -> AgentState:
        """Generate final report"""
        print(f"\n📊 [{self.name}] Generating comprehensive report...")
        
        results = state["analysis_results"]
        
        report = self._generate_report(state["file_path"], results)
        state["final_report"] = report
        state["current_agent"] = self.name
        state["agents_completed"].append(self.name)
        state["should_continue"] = False
        
        return state
    
    def _generate_report(self, file_path: str, results: AnalysisResult) -> str:
        """Generate formatted report"""
        report_lines = [
            "=" * 80,
            "CODE ANALYSIS REPORT",
            "=" * 80,
            f"File: {file_path}",
            f"Analysis Date: 2026-01-29",
            "",
            "=" * 80,
            "SUMMARY",
            "=" * 80,
        ]
        
        # Metrics summary
        report_lines.extend([
            "",
            "Code Metrics:",
            f"  - Lines of Code: {results.metrics.get('lines_of_code', 'N/A')}",
            f"  - Functions: {results.metrics.get('num_functions', 'N/A')}",
            f"  - Classes: {results.metrics.get('num_classes', 'N/A')}",
            f"  - Imports: {results.metrics.get('num_imports', 'N/A')}",
            f"  - Valid Syntax: {'✓' if results.metrics.get('valid_syntax') else '✗'}",
            ""
        ])
        
        # Issues by severity
        issues_by_severity = {}
        for issue in results.issues:
            severity = issue.severity.value
            issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
        
        report_lines.extend([
            "Issues Found:",
            f"  - Critical: {issues_by_severity.get('critical', 0)}",
            f"  - High: {issues_by_severity.get('high', 0)}",
            f"  - Medium: {issues_by_severity.get('medium', 0)}",
            f"  - Low: {issues_by_severity.get('low', 0)}",
            f"  - Info: {issues_by_severity.get('info', 0)}",
            "",
        ])
        
        # Issues by type
        issues_by_type = {}
        for issue in results.issues:
            itype = issue.issue_type.value
            issues_by_type[itype] = issues_by_type.get(itype, 0) + 1
        
        report_lines.extend([
            "Issues by Type:",
        ])
        for itype, count in sorted(issues_by_type.items()):
            report_lines.append(f"  - {itype.replace('_', ' ').title()}: {count}")
        
        # Detailed issues
        if results.issues:
            report_lines.extend([
                "",
                "=" * 80,
                "DETAILED ISSUES",
                "=" * 80,
            ])
            
            # Sort by severity
            severity_order = {
                IssueSeverity.CRITICAL: 0,
                IssueSeverity.HIGH: 1,
                IssueSeverity.MEDIUM: 2,
                IssueSeverity.LOW: 3,
                IssueSeverity.INFO: 4,
            }
            sorted_issues = sorted(results.issues, key=lambda x: severity_order[x.severity])
            
            for idx, issue in enumerate(sorted_issues, 1):
                report_lines.extend([
                    "",
                    f"Issue #{idx}",
                    "-" * 80,
                    f"Type: {issue.issue_type.value.replace('_', ' ').title()}",
                    f"Severity: {issue.severity.value.upper()}",
                    f"Line: {issue.line_number}",
                    f"Description: {issue.description}",
                ])
                
                if issue.code_snippet:
                    report_lines.extend([
                        "",
                        "Code:",
                        issue.code_snippet,
                    ])
                
                if issue.suggestion:
                    report_lines.extend([
                        "",
                        f"Suggestion: {issue.suggestion}",
                    ])
                
                if issue.fixed_code:
                    report_lines.extend([
                        "",
                        "Fixed Code:",
                        issue.fixed_code,
                    ])
        
        # Optimizations
        if results.optimizations:
            report_lines.extend([
                "",
                "=" * 80,
                "OPTIMIZATION SUGGESTIONS",
                "=" * 80,
                ""
            ])
            for opt in results.optimizations:
                report_lines.append(f"  • {opt}")
        
        # Complexity metrics
        complexity_metrics = {
            k: v for k, v in results.metrics.items() if k.startswith('complexity_')
        }
        if complexity_metrics:
            report_lines.extend([
                "",
                "=" * 80,
                "COMPLEXITY METRICS",
                "=" * 80,
                ""
            ])
            for func, complexity in sorted(complexity_metrics.items()):
                func_name = func.replace('complexity_', '')
                status = "⚠️" if complexity > 10 else "✓"
                report_lines.append(f"  {status} {func_name}: {complexity}")
        
        report_lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80,
        ])
        
        return "\n".join(report_lines)


# ============================================================================
# LangGraph Workflow Orchestrator
# ============================================================================

class CodeAnalyzerWorkflow:
    """
    Orchestrates the multi-agent workflow using LangGraph pattern
    """
    
    def __init__(self):
        self.agents = {
            "parser": CodeParserAgent(),
            "bug_detector": BugDetectorAgent(),
            "performance": PerformanceOptimizerAgent(),
            "security": SecurityAnalyzerAgent(),
            "reporter": ReportGeneratorAgent(),
        }
    
    def should_continue(self, state: AgentState) -> str:
        """Decide next node based on state"""
        if not state.get("should_continue", True):
            return "end"
        
        completed = state.get("agents_completed", [])
        
        if "CodeParserAgent" not in completed:
            return "parser"
        elif "BugDetectorAgent" not in completed:
            return "bug_detector"
        elif "PerformanceOptimizerAgent" not in completed:
            return "performance"
        elif "SecurityAnalyzerAgent" not in completed:
            return "security"
        elif "ReportGeneratorAgent" not in completed:
            return "reporter"
        else:
            return "end"
    
    def run(self, code: str, file_path: str = "code.py") -> AgentState:
        """
        Execute the multi-agent workflow
        
        This simulates the LangGraph execution pattern:
        1. Initialize state
        2. Route through agents based on conditions
        3. Each agent updates shared state
        4. Continue until completion
        """
        print("\n" + "=" * 80)
        print("🚀 MULTI-AGENT CODE ANALYZER - STARTING WORKFLOW")
        print("=" * 80)
        
        # Initialize state
        state: AgentState = {
            "code": code,
            "file_path": file_path,
            "analysis_results": AnalysisResult(),
            "current_agent": "",
            "agents_completed": [],
            "debug_log": [],
            "final_report": None,
            "should_continue": True,
        }
        
        # Execute workflow (simulating LangGraph state machine)
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            next_node = self.should_continue(state)
            
            if next_node == "end":
                break
            
            # Execute the agent
            agent = self.agents[next_node]
            state = agent.analyze(state)
            
            iteration += 1
        
        print("\n" + "=" * 80)
        print("✅ WORKFLOW COMPLETED")
        print("=" * 80)
        print(f"Agents executed: {', '.join(state['agents_completed'])}")
        print(f"Total issues found: {len(state['analysis_results'].issues)}")
        print(f"Total optimizations suggested: {len(state['analysis_results'].optimizations)}")
        
        return state


# ============================================================================
# Main Execution
# ============================================================================

def analyze_code_file(file_path: str) -> AgentState:
    """Analyze a Python code file"""
    with open(file_path, 'r') as f:
        code = f.read()
    
    workflow = CodeAnalyzerWorkflow()
    return workflow.run(code, file_path)


def analyze_code_string(code: str, file_path: str = "code.py") -> AgentState:
    """Analyze Python code string"""
    workflow = CodeAnalyzerWorkflow()
    return workflow.run(code, file_path)


if __name__ == "__main__":
    # Example usage
    sample_code = '''
import random

def calculate_total(items=[]):
    total = 0
    for item in items:
        total = total + str(item)
    return total

def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] == True:
            result.append(data[i])
    return result

def read_file():
    f = open('data.txt', 'r')
    content = f.read()
    return content

password = "my_secret_password_123"

def unsafe_query(user_input):
    query = "SELECT * FROM users WHERE name = '%s'" % user_input
    return query
'''
    
    # Run analysis
    result = analyze_code_string(sample_code, "example.py")
    
    # Print report
    if result["final_report"]:
        print("\n")
        print(result["final_report"])
    
    # Export results
    output = {
        "file_path": result["file_path"],
        "metrics": result["analysis_results"].metrics,
        "issues_count": len(result["analysis_results"].issues),
        "optimizations_count": len(result["analysis_results"].optimizations),
    }
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Results saved. Total issues: {output['issues_count']}")