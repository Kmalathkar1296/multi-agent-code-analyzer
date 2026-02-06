"""
Multi-Language Code Analyzer
Supports Python, JavaScript, Java, SQL, TypeScript, and more
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    SQL = "sql"
    UNKNOWN = "unknown"


@dataclass
class Issue:
    """Universal issue format for all languages"""
    language: str
    type: str
    severity: str
    line: int
    description: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


class JavaScriptAnalyzer:
    """Analyzer for JavaScript/TypeScript code"""
    
    def analyze(self, code: str, file_path: str) -> Dict:
        """Analyze JavaScript code"""
        issues = []
        lines = code.split('\n')
        
        # Security issues
        self._check_eval(code, lines, issues)
        self._check_console_log(code, lines, issues)
        self._check_sql_injection(code, lines, issues)
        self._check_xss(code, lines, issues)
        
        # Code quality
        self._check_var_usage(code, lines, issues)
        self._check_equality(code, lines, issues)
        self._check_async_await(code, lines, issues)
        
        # Performance
        self._check_loops(code, lines, issues)
        
        return {
            "file": file_path,
            "language": "javascript",
            "issues": [self._format_issue(i) for i in issues],
            "metrics": self._calculate_metrics(code, lines)
        }
    
    def _check_eval(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for eval() usage"""
        for i, line in enumerate(lines, 1):
            if re.search(r'\beval\s*\(', line):
                issues.append(Issue(
                    language="javascript",
                    type="security",
                    severity="critical",
                    line=i,
                    description="Use of eval() is dangerous - allows arbitrary code execution",
                    suggestion="Avoid eval(). Use JSON.parse() for JSON or other safer alternatives"
                ))
    
    def _check_console_log(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for console.log in production code"""
        for i, line in enumerate(lines, 1):
            if 'console.log' in line and not line.strip().startswith('//'):
                issues.append(Issue(
                    language="javascript",
                    type="code_smell",
                    severity="low",
                    line=i,
                    description="console.log() should be removed from production code",
                    suggestion="Remove console.log or use proper logging library"
                ))
    
    def _check_sql_injection(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for SQL injection vulnerabilities"""
        for i, line in enumerate(lines, 1):
            if re.search(r'(SELECT|INSERT|UPDATE|DELETE).*\+.*\${', line, re.IGNORECASE):
                issues.append(Issue(
                    language="javascript",
                    type="security",
                    severity="critical",
                    line=i,
                    description="Possible SQL injection vulnerability - using string concatenation",
                    suggestion="Use parameterized queries or prepared statements"
                ))
    
    def _check_xss(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for XSS vulnerabilities"""
        for i, line in enumerate(lines, 1):
            if re.search(r'innerHTML\s*=\s*.*\${', line) or re.search(r'dangerouslySetInnerHTML', line):
                issues.append(Issue(
                    language="javascript",
                    type="security",
                    severity="high",
                    line=i,
                    description="Potential XSS vulnerability - inserting user data into HTML",
                    suggestion="Sanitize user input or use textContent instead of innerHTML"
                ))
    
    def _check_var_usage(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for var instead of let/const"""
        for i, line in enumerate(lines, 1):
            if re.search(r'\bvar\s+\w+', line):
                issues.append(Issue(
                    language="javascript",
                    type="style",
                    severity="medium",
                    line=i,
                    description="Use 'let' or 'const' instead of 'var'",
                    suggestion="Prefer const for constants and let for variables"
                ))
    
    def _check_equality(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for == instead of ==="""
        for i, line in enumerate(lines, 1):
            if re.search(r'(?<![=!])={2}(?!=)', line):
                issues.append(Issue(
                    language="javascript",
                    type="code_smell",
                    severity="medium",
                    line=i,
                    description="Use === instead of == for strict equality",
                    suggestion="Use === and !== for type-safe comparisons"
                ))
    
    def _check_async_await(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for missing async/await"""
        for i, line in enumerate(lines, 1):
            if '.then(' in line and 'catch' not in code[code.find('.then('):code.find('.then(')+100]:
                issues.append(Issue(
                    language="javascript",
                    type="logic_error",
                    severity="medium",
                    line=i,
                    description="Promise without .catch() - unhandled promise rejection",
                    suggestion="Add .catch() or use try/catch with async/await"
                ))
    
    def _check_loops(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for performance issues in loops"""
        for i, line in enumerate(lines, 1):
            if re.search(r'for\s*\(.*\.length', line):
                issues.append(Issue(
                    language="javascript",
                    type="performance",
                    severity="low",
                    line=i,
                    description="Accessing .length in loop condition - cache it outside",
                    suggestion="Cache array.length before loop for better performance"
                ))
    
    def _calculate_metrics(self, code: str, lines: List[str]) -> Dict:
        """Calculate code metrics"""
        return {
            "lines_of_code": len(lines),
            "num_functions": len(re.findall(r'function\s+\w+|=>\s*{', code)),
            "num_classes": len(re.findall(r'class\s+\w+', code))
        }
    
    def _format_issue(self, issue: Issue) -> Dict:
        """Format issue for JSON output"""
        return {
            "type": issue.type,
            "severity": issue.severity,
            "line": issue.line,
            "description": issue.description,
            "suggestion": issue.suggestion
        }


class JavaAnalyzer:
    """Analyzer for Java code"""
    
    def analyze(self, code: str, file_path: str) -> Dict:
        """Analyze Java code"""
        issues = []
        lines = code.split('\n')
        
        # Security
        self._check_sql_injection(code, lines, issues)
        self._check_serialization(code, lines, issues)
        self._check_random(code, lines, issues)
        
        # Code quality
        self._check_exception_handling(code, lines, issues)
        self._check_nulls(code, lines, issues)
        self._check_string_concatenation(code, lines, issues)
        
        return {
            "file": file_path,
            "language": "java",
            "issues": [self._format_issue(i) for i in issues],
            "metrics": self._calculate_metrics(code, lines)
        }
    
    def _check_sql_injection(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for SQL injection"""
        for i, line in enumerate(lines, 1):
            if re.search(r'executeQuery\s*\(\s*["\'].*\+', line) or \
               re.search(r'createQuery\s*\(\s*["\'].*\+', line):
                issues.append(Issue(
                    language="java",
                    type="security",
                    severity="critical",
                    line=i,
                    description="SQL injection vulnerability - using string concatenation",
                    suggestion="Use PreparedStatement with parameterized queries"
                ))
    
    def _check_serialization(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for unsafe deserialization"""
        for i, line in enumerate(lines, 1):
            if 'ObjectInputStream' in line and 'readObject' in code:
                issues.append(Issue(
                    language="java",
                    type="security",
                    severity="high",
                    line=i,
                    description="Potential unsafe deserialization",
                    suggestion="Validate serialized objects before deserialization"
                ))
    
    def _check_random(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for insecure random"""
        for i, line in enumerate(lines, 1):
            if re.search(r'new\s+Random\s*\(', line):
                issues.append(Issue(
                    language="java",
                    type="security",
                    severity="medium",
                    line=i,
                    description="Using Random for security-sensitive operations",
                    suggestion="Use SecureRandom for cryptographic operations"
                ))
    
    def _check_exception_handling(self, code: str, lines: List[str], issues: List[Issue]):
        """Check exception handling"""
        for i, line in enumerate(lines, 1):
            if re.search(r'catch\s*\(\s*Exception\s+\w+\s*\)\s*\{?\s*\}', line):
                issues.append(Issue(
                    language="java",
                    type="code_smell",
                    severity="medium",
                    line=i,
                    description="Empty catch block - exceptions are silently ignored",
                    suggestion="At minimum, log the exception"
                ))
    
    def _check_nulls(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for potential NPE"""
        for i, line in enumerate(lines, 1):
            if '== null' in line or '!= null' in line:
                issues.append(Issue(
                    language="java",
                    type="code_smell",
                    severity="low",
                    line=i,
                    description="Null check - consider using Optional or null-safe operators",
                    suggestion="Use Optional<T> or Objects.requireNonNull()"
                ))
    
    def _check_string_concatenation(self, code: str, lines: List[str], issues: List[Issue]):
        """Check string concatenation in loops"""
        in_loop = False
        for i, line in enumerate(lines, 1):
            if re.search(r'\b(for|while)\s*\(', line):
                in_loop = True
            if in_loop and ('+=' in line or '= ' in line) and '"' in line:
                issues.append(Issue(
                    language="java",
                    type="performance",
                    severity="medium",
                    line=i,
                    description="String concatenation in loop",
                    suggestion="Use StringBuilder for better performance"
                ))
            if '}' in line:
                in_loop = False
    
    def _calculate_metrics(self, code: str, lines: List[str]) -> Dict:
        """Calculate metrics"""
        return {
            "lines_of_code": len(lines),
            "num_methods": len(re.findall(r'(public|private|protected)\s+\w+\s+\w+\s*\(', code)),
            "num_classes": len(re.findall(r'class\s+\w+', code))
        }
    
    def _format_issue(self, issue: Issue) -> Dict:
        return {
            "type": issue.type,
            "severity": issue.severity,
            "line": issue.line,
            "description": issue.description,
            "suggestion": issue.suggestion
        }


class SQLAnalyzer:
    """Analyzer for SQL code"""
    
    def analyze(self, code: str, file_path: str) -> Dict:
        """Analyze SQL code"""
        issues = []
        lines = code.split('\n')
        
        # Security
        self._check_sql_injection_patterns(code, lines, issues)
        
        # Performance
        self._check_select_star(code, lines, issues)
        self._check_missing_indexes(code, lines, issues)
        self._check_functions_in_where(code, lines, issues)
        
        # Best practices
        self._check_implicit_joins(code, lines, issues)
        
        return {
            "file": file_path,
            "language": "sql",
            "issues": [self._format_issue(i) for i in issues],
            "metrics": self._calculate_metrics(code, lines)
        }
    
    def _check_sql_injection_patterns(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for SQL injection patterns in stored procedures"""
        for i, line in enumerate(lines, 1):
            if re.search(r"EXECUTE\s+.*\+|EXEC\s+.*\+", line, re.IGNORECASE):
                issues.append(Issue(
                    language="sql",
                    type="security",
                    severity="critical",
                    line=i,
                    description="Dynamic SQL with concatenation - SQL injection risk",
                    suggestion="Use parameterized queries with sp_executesql"
                ))
    
    def _check_select_star(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for SELECT *"""
        for i, line in enumerate(lines, 1):
            if re.search(r'SELECT\s+\*', line, re.IGNORECASE):
                issues.append(Issue(
                    language="sql",
                    type="performance",
                    severity="medium",
                    line=i,
                    description="SELECT * is inefficient and can break code",
                    suggestion="Specify only the columns you need"
                ))
    
    def _check_missing_indexes(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for WHERE clauses that might need indexes"""
        for i, line in enumerate(lines, 1):
            if re.search(r'WHERE.*LIKE\s+["\']%', line, re.IGNORECASE):
                issues.append(Issue(
                    language="sql",
                    type="performance",
                    severity="high",
                    line=i,
                    description="LIKE with leading wildcard prevents index usage",
                    suggestion="Avoid leading wildcards or use full-text search"
                ))
    
    def _check_functions_in_where(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for functions on indexed columns in WHERE"""
        for i, line in enumerate(lines, 1):
            if re.search(r'WHERE.*\w+\s*\(.*\)\s*=', line, re.IGNORECASE):
                issues.append(Issue(
                    language="sql",
                    type="performance",
                    severity="medium",
                    line=i,
                    description="Function on column in WHERE clause prevents index usage",
                    suggestion="Rewrite to avoid function on indexed column"
                ))
    
    def _check_implicit_joins(self, code: str, lines: List[str], issues: List[Issue]):
        """Check for implicit joins"""
        for i, line in enumerate(lines, 1):
            if re.search(r'FROM.*,.*WHERE', code[max(0, code.find(line)-200):code.find(line)+200], re.IGNORECASE):
                issues.append(Issue(
                    language="sql",
                    type="code_smell",
                    severity="low",
                    line=i,
                    description="Implicit join using comma - use explicit JOIN",
                    suggestion="Use INNER JOIN, LEFT JOIN etc. for clarity"
                ))
    
    def _calculate_metrics(self, code: str, lines: List[str]) -> Dict:
        return {
            "lines_of_code": len(lines),
            "num_queries": len(re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', code, re.IGNORECASE)),
            "num_procedures": len(re.findall(r'CREATE\s+PROCEDURE', code, re.IGNORECASE))
        }
    
    def _format_issue(self, issue: Issue) -> Dict:
        return {
            "type": issue.type,
            "severity": issue.severity,
            "line": issue.line,
            "description": issue.description,
            "suggestion": issue.suggestion
        }


def analyze_code(code: str, language: str, file_path: str = "code") -> Dict:
    """
    Analyze code in any supported language
    
    Args:
        code: Source code to analyze
        language: Programming language (python, javascript, java, sql)
        file_path: File path for reporting
    
    Returns:
        Analysis results dictionary
    """
    if language in ['javascript', 'typescript']:
        analyzer = JavaScriptAnalyzer()
        return analyzer.analyze(code, file_path)
    elif language == 'java':
        analyzer = JavaAnalyzer()
        return analyzer.analyze(code, file_path)
    elif language == 'sql':
        analyzer = SQLAnalyzer()
        return analyzer.analyze(code, file_path)
    elif language == 'python':
        # Use existing Python analyzer
        from code_analyzer_system import analyze_code_string
        result = analyze_code_string(code, file_path)
        return {
            "file": file_path,
            "language": "python",
            "issues": [
                {
                    "type": i.issue_type.value,
                    "severity": i.severity.value,
                    "line": i.line_number,
                    "description": i.description,
                    "suggestion": i.suggestion
                }
                for i in result["analysis_results"].issues
            ],
            "metrics": result["analysis_results"].metrics
        }
    else:
        return {
            "file": file_path,
            "language": language,
            "issues": [],
            "metrics": {},
            "error": f"Language '{language}' not yet supported"
        }


if __name__ == "__main__":
    # Demo
    print("Multi-Language Analyzer Demo\n")
    
    # JavaScript example
    js_code = """
    function login(username, password) {
        var query = "SELECT * FROM users WHERE user='" + username + "'";
        eval(userInput);
        console.log("Debug: " + query);
    }
    """
    
    result = analyze_code(js_code, "javascript", "login.js")
    print(f"JavaScript: Found {len(result['issues'])} issues")
    
    # SQL example
    sql_code = """
    SELECT * FROM users WHERE UPPER(email) = 'TEST@EXAMPLE.COM';
    SELECT name FROM products WHERE name LIKE '%search%';
    """
    
    result = analyze_code(sql_code, "sql", "query.sql")
    print(f"SQL: Found {len(result['issues'])} issues")