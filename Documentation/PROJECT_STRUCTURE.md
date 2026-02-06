# Project Structure - Multi-Agent Code Analyzer

## Directory Layout

```
code-analyzer/
├── README.md                           # Main documentation
├── USAGE_GUIDE.md                      # Detailed usage examples
├── requirements.txt                     # Python dependencies
├── config.py                           # Configuration management
├── code_analyzer_system.py             # Main system (standalone, no deps)
├── langgraph_implementation.py         # LangGraph integration template
├── cli.py                              # Command-line interface
├── quick_start.py                      # Quick start demo
│
├── test_examples/                      # Example files for testing
│   └── buggy_code.py                   # Example with various issues
│
└── docs/                               # Additional documentation
    ├── architecture.md
    ├── agent_details.md
    └── api_reference.md
```

## File Descriptions

### Core Files

#### `code_analyzer_system.py` (Main System)
The complete standalone implementation of the multi-agent analyzer.

**Components:**
- `AgentState`: Shared state TypedDict for agents
- `CodeIssue`: Data class for detected issues
- `AnalysisResult`: Results container
- `CodeParserAgent`: Syntax and structure analysis
- `BugDetectorAgent`: Logic error detection
- `PerformanceOptimizerAgent`: Performance analysis
- `SecurityAnalyzerAgent`: Security vulnerability detection
- `ReportGeneratorAgent`: Report generation
- `CodeAnalyzerWorkflow`: Workflow orchestrator

**Usage:**
```python
from code_analyzer_system import analyze_code_file
result = analyze_code_file("script.py")
print(result["final_report"])
```

**No dependencies required!** Works with just Python standard library.

---

#### `langgraph_implementation.py` (LangGraph Template)
Template for integrating with LangGraph when you have network access.

**Features:**
- Proper StateGraph implementation
- Conditional edge routing
- Human-in-the-loop patterns
- Integration with Claude API

**Requirements:**
```bash
pip install langgraph langchain langchain-anthropic
```

---

#### `cli.py` (Command Line Interface)
Full-featured CLI for the analyzer.

**Features:**
- Single file or directory analysis
- Multiple output formats (text, JSON, HTML)
- Severity filtering
- Recursive directory scanning
- CI/CD integration support

**Usage:**
```bash
python cli.py script.py
python cli.py src/ --recursive --format json
python cli.py file.py --severity critical,high --output report.txt
```

---

#### `config.py` (Configuration)
Configuration management for customizing analyzer behavior.

**Predefined Configs:**
- `DEFAULT_CONFIG`: Balanced settings
- `STRICT_CONFIG`: Maximum strictness
- `PERMISSIVE_CONFIG`: Relaxed for prototyping
- `SECURITY_FOCUSED_CONFIG`: Security only
- `PERFORMANCE_FOCUSED_CONFIG`: Performance only

**Usage:**
```python
from config import load_config
config = load_config("strict")
```

---

#### `quick_start.py` (Demo)
Interactive demo showcasing system capabilities.

**Demos:**
1. Basic code analysis
2. Security-focused analysis
3. Performance analysis
4. Complete report generation

**Usage:**
```bash
python quick_start.py
```

---

### Test Files

#### `test_examples/buggy_code.py`
Example Python file containing various intentional issues:
- Mutable default arguments
- Resource leaks
- SQL injection vulnerabilities
- Hardcoded secrets
- Performance anti-patterns
- High complexity functions
- Style issues

Use this to test the analyzer or as a reference for what it can detect.

---

## Documentation Files

### `README.md`
- Overview and architecture
- Quick start guide
- Feature list
- Installation instructions
- Basic usage examples
- LangGraph integration guide
- Extension points

### `USAGE_GUIDE.md`
- Comprehensive usage examples
- Advanced patterns
- CLI reference
- Configuration guide
- Integration examples
- Best practices
- Troubleshooting

---

## Key Components Deep Dive

### State Management
The system uses TypedDict for type-safe state sharing between agents:

```python
class AgentState(TypedDict):
    code: str                                    # Source code
    file_path: str                              # File path
    analysis_results: AnalysisResult            # Accumulated results
    current_agent: str                          # Current executing agent
    agents_completed: List[str]                 # Completed agents
    debug_log: List[str]                        # Debug messages
    final_report: Optional[str]                 # Final report
    should_continue: bool                       # Continue flag
```

### Issue Classification

**Issue Types:**
- `SYNTAX_ERROR`: Invalid Python syntax
- `LOGIC_ERROR`: Programming logic errors
- `PERFORMANCE`: Performance bottlenecks
- `SECURITY`: Security vulnerabilities
- `CODE_SMELL`: Suboptimal patterns
- `STYLE`: Style and documentation issues
- `COMPLEXITY`: High complexity warnings

**Severity Levels:**
- `CRITICAL`: Must fix (security, syntax)
- `HIGH`: Should fix soon (bugs, leaks)
- `MEDIUM`: Should address (smells, performance)
- `LOW`: Nice to have (style, docs)
- `INFO`: Informational

### Agent Workflow

```
1. CodeParserAgent
   ↓ (validates syntax, analyzes structure)
2. BugDetectorAgent
   ↓ (detects logic errors, bugs)
3. PerformanceOptimizerAgent
   ↓ (finds performance issues)
4. SecurityAnalyzerAgent
   ↓ (checks security vulnerabilities)
5. ReportGeneratorAgent
   ↓ (generates comprehensive report)
   → Output
```

Each agent:
1. Receives the shared state
2. Performs its analysis
3. Updates the results
4. Adds to debug log
5. Returns updated state

---

## Extension Guide

### Adding a New Agent

```python
class CustomAgent:
    def __init__(self):
        self.name = "CustomAgent"
    
    def analyze(self, state: AgentState) -> AgentState:
        code = state["code"]
        results = state["analysis_results"]
        
        # Your analysis logic here
        # Add issues to results.issues
        # Add metrics to results.metrics
        
        state["agents_completed"].append(self.name)
        return state

# Add to workflow
workflow = CodeAnalyzerWorkflow()
workflow.agents["custom"] = CustomAgent()
```

### Adding Custom Detection Rules

```python
class EnhancedBugDetector(BugDetectorAgent):
    def analyze(self, state):
        # Call parent
        state = super().analyze(state)
        
        # Add custom checks
        self._check_custom_pattern(state["code"], state["analysis_results"])
        
        return state
    
    def _check_custom_pattern(self, code, results):
        # Your custom detection logic
        pass
```

### Custom Report Format

```python
class JSONReportGenerator(ReportGeneratorAgent):
    def _generate_report(self, file_path, results):
        import json
        return json.dumps({
            "file": file_path,
            "issues": [asdict(i) for i in results.issues],
            "metrics": results.metrics
        }, indent=2)
```

---

## Integration Examples

### Pre-commit Hook

```python
# .git/hooks/pre-commit
#!/usr/bin/env python3
import sys
from code_analyzer_system import analyze_code_file, IssueSeverity

files = get_staged_python_files()
has_errors = False

for f in files:
    result = analyze_code_file(f)
    critical = [i for i in result["analysis_results"].issues 
                if i.severity == IssueSeverity.CRITICAL]
    if critical:
        print(f"❌ {f} has critical issues")
        has_errors = True

sys.exit(1 if has_errors else 0)
```

### CI/CD Pipeline

```yaml
# .github/workflows/code-quality.yml
name: Code Quality
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Code Analyzer
        run: |
          python cli.py src/ --recursive --format json --output results.json
          python -c "
          import json, sys
          with open('results.json') as f:
              data = json.load(f)
          if data['summary']['total_issues'] > 0:
              print('❌ Issues found')
              sys.exit(1)
          "
```

### IDE Integration

```python
# For VS Code extension or similar
def analyze_on_save(file_path):
    from code_analyzer_system import analyze_code_file
    
    result = analyze_code_file(file_path)
    
    # Convert to IDE diagnostic format
    diagnostics = []
    for issue in result["analysis_results"].issues:
        diagnostics.append({
            "range": {"start": {"line": issue.line_number, "character": 0}},
            "severity": severity_to_ide(issue.severity),
            "message": issue.description,
            "source": "code-analyzer"
        })
    
    return diagnostics
```

---

## Performance Considerations

### Single File
- Typical analysis time: 50-200ms
- Memory usage: ~10-20MB

### Large Codebase (1000+ files)
- Use parallel processing:
```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor() as executor:
    results = executor.map(analyze_code_file, files)
```

### Optimizations
1. Cache AST parsing results
2. Skip test files if appropriate
3. Use incremental analysis (only changed files)
4. Implement result caching

---

## Testing

### Unit Tests (Example)

```python
import unittest
from code_analyzer_system import analyze_code_string, IssueType

class TestCodeAnalyzer(unittest.TestCase):
    def test_detects_mutable_default(self):
        code = "def func(x=[]):\n    pass"
        result = analyze_code_string(code)
        
        has_issue = any(
            i.issue_type == IssueType.LOGIC_ERROR and
            "mutable" in i.description.lower()
            for i in result["analysis_results"].issues
        )
        
        self.assertTrue(has_issue)
    
    def test_detects_hardcoded_secret(self):
        code = 'password = "secret123"'
        result = analyze_code_string(code)
        
        security_issues = [
            i for i in result["analysis_results"].issues
            if i.issue_type == IssueType.SECURITY
        ]
        
        self.assertTrue(len(security_issues) > 0)
```

---

## Roadmap

### Planned Features
- [ ] Auto-fix generation for common issues
- [ ] ML-based bug prediction
- [ ] Integration with more IDEs
- [ ] Team dashboard
- [ ] Historical analysis trends
- [ ] Custom rule language
- [ ] Plugin system
- [ ] Real-time analysis

### Community Extensions
- IDE plugins
- CI/CD integrations
- Custom reporters
- Language support beyond Python

---

## Contributing

To extend the system:

1. **Add detection rules**: Extend agent classes
2. **New agents**: Create new agent classes
3. **Custom reports**: Extend ReportGeneratorAgent
4. **Integrations**: Create adapters for your tools
5. **Documentation**: Add to USAGE_GUIDE.md

---

## License

This is a reference implementation for educational purposes.

## Support

- Check README.md for basics
- Read USAGE_GUIDE.md for examples
- Examine test_examples/ for patterns
- Review code comments for details

---

**Last Updated:** 2026-01-29
**Version:** 1.0.0