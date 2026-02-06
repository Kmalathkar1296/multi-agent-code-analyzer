"""
GitHub Integration Module
Enables analyzing code directly from GitHub repositories
"""

import os
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import subprocess


class GitHubAnalyzer:
    """Analyze code from GitHub repositories"""
    
    def __init__(self):
        self.temp_dir = None
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.sql': 'sql',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
        }
    
    def analyze_github_url(self, github_url: str, branch: str = "main") -> Dict:
        """
        Analyze code from a GitHub repository
        
        Args:
            github_url: GitHub repository URL (e.g., https://github.com/user/repo)
            branch: Branch to analyze (default: main)
        
        Returns:
            Dictionary with analysis results for all supported files
        """
        print(f"\n🔗 GitHub Analyzer - Processing: {github_url}")
        print(f"   Branch: {branch}")
        
        # Validate URL
        if not self._is_valid_github_url(github_url):
            raise ValueError(f"Invalid GitHub URL: {github_url}")
        
        # Extract repo info
        repo_info = self._parse_github_url(github_url)
        print(f"   Repository: {repo_info['owner']}/{repo_info['repo']}")
        
        # Clone repository
        repo_path = self._clone_repository(github_url, branch)
        
        try:
            # Find all supported files
            files = self._find_code_files(repo_path)
            print(f"\n📁 Found {len(files)} code files to analyze")
            
            # Analyze each file
            results = self._analyze_files(files, repo_path)
            
            # Generate summary
            summary = self._generate_summary(results, repo_info)
            
            return {
                "repository": repo_info,
                "branch": branch,
                "summary": summary,
                "files": results
            }
        
        finally:
            # Cleanup
            self._cleanup()
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Check if URL is a valid GitHub URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc in ['github.com', 'www.github.com']
        except:
            return False
    
    def _parse_github_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL to extract owner and repo"""
        # Clean URL
        url = url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        # Parse
        parsed = urlparse(url)
        parts = parsed.path.strip('/').split('/')
        
        if len(parts) < 2:
            raise ValueError(f"Cannot parse repository from URL: {url}")
        
        return {
            "owner": parts[0],
            "repo": parts[1],
            "url": url
        }
    
    def _clone_repository(self, url: str, branch: str) -> str:
        """Clone GitHub repository to temporary directory"""
        self.temp_dir = tempfile.mkdtemp(prefix="github_analyzer_")
        repo_path = os.path.join(self.temp_dir, "repo")
        
        print(f"\n📦 Cloning repository...")
        print(f"   Destination: {repo_path}")
        
        try:
            # Try git clone first
            cmd = ["git", "clone", "--depth", "1", "-b", branch, url, repo_path]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"   ✓ Clone successful via git")
                return repo_path
            else:
                print(f"   ⚠️  Git clone failed: {result.stderr}")
                raise Exception("Git clone failed")
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            # Fallback: download as ZIP (implement if needed)
            print(f"   ℹ️  Git not available or clone failed")
            print(f"   💡 Alternative: Download the repo manually and use local path")
            raise Exception(
                f"Cannot clone repository. Please:\n"
                f"1. Install git, or\n"
                f"2. Download the repo manually and analyze local path:\n"
                f"   python cli.py /path/to/downloaded/repo --recursive"
            )
    
    def _find_code_files(self, repo_path: str) -> List[Tuple[str, str]]:
        """Find all supported code files in repository"""
        files = []
        
        # Directories to skip
        skip_dirs = {
            '.git', '__pycache__', 'node_modules', 'venv', '.venv',
            'build', 'dist', '.pytest_cache', '.mypy_cache', 'target',
            'bin', 'obj', '.idea', '.vscode'
        }
        
        for root, dirs, filenames in os.walk(repo_path):
            # Skip hidden and build directories
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
            
            for filename in filenames:
                ext = os.path.splitext(filename)[1]
                if ext in self.supported_extensions:
                    file_path = os.path.join(root, filename)
                    language = self.supported_extensions[ext]
                    
                    # Get relative path for reporting
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    files.append((file_path, language, rel_path))
        
        return files
    
    def _analyze_files(self, files: List[Tuple[str, str, str]], repo_path: str) -> List[Dict]:
        """Analyze all files and return results"""
        results = []
        
        for idx, (file_path, language, rel_path) in enumerate(files, 1):
            print(f"\n   [{idx}/{len(files)}] Analyzing: {rel_path}")
            print(f"       Language: {language}")
            
            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                
                # Analyze based on language
                if language == 'python':
                    from code_analyzer_system import analyze_code_string
                    result = analyze_code_string(code, rel_path)
                    analysis = self._format_python_results(result, rel_path)
                else:
                    # Use multi-language analyzer
                    from multi_language_analyzer import analyze_code
                    analysis = analyze_code(code, language, rel_path)
                
                results.append(analysis)
                
                # Show quick stats
                issues = analysis.get('issues', [])
                critical = len([i for i in issues if i.get('severity') == 'critical'])
                high = len([i for i in issues if i.get('severity') == 'high'])
                
                if critical > 0 or high > 0:
                    print(f"       ⚠️  Critical: {critical}, High: {high}")
                else:
                    print(f"       ✓ No critical issues")
            
            except Exception as e:
                print(f"       ✗ Error: {str(e)}")
                results.append({
                    "file": rel_path,
                    "language": language,
                    "error": str(e),
                    "issues": []
                })
        
        return results
    
    def _format_python_results(self, result: Dict, file_path: str) -> Dict:
        """Format Python analysis results to standard format"""
        issues = []
        for issue in result["analysis_results"].issues:
            issues.append({
                "type": issue.issue_type.value,
                "severity": issue.severity.value,
                "line": issue.line_number,
                "description": issue.description,
                "suggestion": issue.suggestion
            })
        
        return {
            "file": file_path,
            "language": "python",
            "metrics": result["analysis_results"].metrics,
            "issues": issues,
            "optimizations": result["analysis_results"].optimizations
        }
    
    def _generate_summary(self, results: List[Dict], repo_info: Dict) -> Dict:
        """Generate summary statistics"""
        total_files = len(results)
        total_issues = sum(len(r.get('issues', [])) for r in results)
        
        # Count by severity
        by_severity = {}
        by_language = {}
        by_type = {}
        
        for result in results:
            language = result.get('language', 'unknown')
            by_language[language] = by_language.get(language, 0) + 1
            
            for issue in result.get('issues', []):
                severity = issue.get('severity', 'unknown')
                by_severity[severity] = by_severity.get(severity, 0) + 1
                
                issue_type = issue.get('type', 'unknown')
                by_type[issue_type] = by_type.get(issue_type, 0) + 1
        
        return {
            "repository": f"{repo_info['owner']}/{repo_info['repo']}",
            "total_files": total_files,
            "total_issues": total_issues,
            "by_severity": by_severity,
            "by_language": by_language,
            "by_type": by_type
        }
    
    def _cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"\n🧹 Cleanup complete")


def analyze_github_repo(url: str, branch: str = "main", output_format: str = "text") -> str:
    """
    Convenience function to analyze a GitHub repository
    
    Args:
        url: GitHub repository URL
        branch: Branch to analyze (default: main)
        output_format: Output format ('text', 'json', 'html')
    
    Returns:
        Formatted analysis report
    """
    analyzer = GitHubAnalyzer()
    results = analyzer.analyze_github_url(url, branch)
    
    if output_format == 'json':
        return json.dumps(results, indent=2)
    elif output_format == 'html':
        return _generate_html_report(results)
    else:
        return _generate_text_report(results)


def _generate_text_report(results: Dict) -> str:
    """Generate text report for GitHub analysis"""
    lines = []
    
    lines.append("=" * 80)
    lines.append("GITHUB REPOSITORY ANALYSIS REPORT")
    lines.append("=" * 80)
    lines.append(f"Repository: {results['summary']['repository']}")
    lines.append(f"Branch: {results['branch']}")
    lines.append("")
    
    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"Files Analyzed: {results['summary']['total_files']}")
    lines.append(f"Total Issues: {results['summary']['total_issues']}")
    lines.append("")
    
    lines.append("Files by Language:")
    for lang, count in results['summary']['by_language'].items():
        lines.append(f"  - {lang.title()}: {count}")
    lines.append("")
    
    lines.append("Issues by Severity:")
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        count = results['summary']['by_severity'].get(severity, 0)
        if count > 0:
            lines.append(f"  - {severity.upper()}: {count}")
    lines.append("")
    
    lines.append("Issues by Type:")
    for itype, count in results['summary']['by_type'].items():
        lines.append(f"  - {itype.replace('_', ' ').title()}: {count}")
    lines.append("")
    
    # Top issues
    lines.append("=" * 80)
    lines.append("FILES WITH MOST ISSUES")
    lines.append("=" * 80)
    
    files_with_issues = [f for f in results['files'] if len(f.get('issues', [])) > 0]
    files_with_issues.sort(key=lambda x: len(x.get('issues', [])), reverse=True)
    
    for file_result in files_with_issues[:10]:  # Top 10
        issues = file_result.get('issues', [])
        critical = len([i for i in issues if i.get('severity') == 'critical'])
        high = len([i for i in issues if i.get('severity') == 'high'])
        
        lines.append(f"\n📄 {file_result['file']}")
        lines.append(f"   Language: {file_result['language']}")
        lines.append(f"   Total Issues: {len(issues)}")
        if critical > 0:
            lines.append(f"   ⚠️  Critical: {critical}, High: {high}")
    
    lines.append("\n" + "=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def _generate_html_report(results: Dict) -> str:
    """Generate HTML report for GitHub analysis"""
    # Similar to existing HTML generator but for GitHub results
    # Implementation similar to cli.py HTML output
    return f"<html><body><h1>Report for {results['summary']['repository']}</h1></body></html>"


if __name__ == "__main__":
    # Example usage
    print("\n" + "=" * 80)
    print("GITHUB ANALYZER - DEMO")
    print("=" * 80)
    print("\nUsage:")
    print('  python github_integration.py "https://github.com/user/repo"')
    print("\nOr in code:")
    print('  from github_integration import analyze_github_repo')
    print('  report = analyze_github_repo("https://github.com/user/repo")')
    print('  print(report)')