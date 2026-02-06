# 🚀 Getting Started with Multi-Agent Code Analyzer

Welcome! This guide will get you up and running with the Multi-Agent Code Analyzer in 5 minutes.

## 📦 What You Got

A complete multi-agent system built with the LangGraph architecture pattern that:
- ✅ Automatically detects bugs and issues in Python code
- ✅ Analyzes security vulnerabilities
- ✅ Identifies performance bottlenecks
- ✅ Suggests optimizations
- ✅ Generates comprehensive reports

**Best part?** The core system has **zero dependencies** - it works with just Python!

## ⚡ Quick Start (30 seconds)

### Option 1: Try it Right Now

```bash
# Run the demo
python quick_start.py

# Or analyze an example file
python code_analyzer_system.py
```

### Option 2: Analyze Your Code

```bash
# Analyze a single file
python -c "
from code_analyzer_system import analyze_code_file
result = analyze_code_file('your_script.py')
print(result['final_report'])
"

# Or use the CLI
python cli.py your_script.py
```

## 📂 What's Included

```
code-analyzer-system/
├── 📄 code_analyzer_system.py    ← Core system (start here!)
├── 📄 quick_start.py              ← Interactive demo
├── 📄 cli.py                      ← Command-line interface
├── 📄 langgraph_implementation.py ← LangGraph template
├── 📄 config.py                   ← Configuration options
├── 📄 README.md                   ← Full documentation
├── 📄 USAGE_GUIDE.md             ← Usage examples
├── 📄 PROJECT_STRUCTURE.md       ← Architecture details
├── 📄 requirements.txt           ← Optional dependencies
└── 📁 test_examples/             ← Example files
    └── buggy_code.py             ← Test file with issues
```

## 🎯 Choose Your Path

### Path 1: Just Want to Analyze Code? (Beginner)

```python
from code_analyzer_system import analyze_code_file

# Analyze any Python file
result = analyze_code_file("script.py")

# Get the report
print(result["final_report"])

# Access specific data
issues = result["analysis_results"].issues
print(f"Found {len(issues)} issues")
```

**That's it!** No installation, no configuration needed.

---

### Path 2: Want the CLI? (Intermediate)

```bash
# Basic usage
python cli.py script.py

# With options
python cli.py script.py --format json --output report.json
python cli.py src/ --recursive --severity critical,high

# See all options
python cli.py --help
```

---

### Path 3: Want to Use LangGraph? (Advanced)

First, install dependencies:
```bash
pip install langgraph langchain langchain-anthropic
```

Then check `langgraph_implementation.py` for the template.

You'll need an Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

---

## 🎮 Try the Demo

The interactive demo shows what the system can do:

```bash
python quick_start.py
```

This runs 4 demos:
1. **Basic Analysis** - See how it detects various issues
2. **Security Focus** - Security vulnerability detection
3. **Performance Analysis** - Performance bottleneck identification
4. **Complete Report** - Full analysis with metrics

---

## 🔍 What It Detects

### 🐛 Bugs & Logic Errors
```python
# Mutable default argument
def append_item(item, my_list=[]):  # ❌ Detected!
    my_list.append(item)

# Resource leak
f = open('file.txt')  # ❌ Should use 'with'
data = f.read()
```

### 🔒 Security Issues
```python
# Hardcoded secrets
password = "admin123"  # ❌ Critical!

# SQL injection
query = f"SELECT * FROM users WHERE name = '{user_input}'"  # ❌

# Dangerous functions
result = eval(user_input)  # ❌ Never do this!
```

### ⚡ Performance Problems
```python
# String concatenation in loop
result = ""
for item in items:
    result = result + item  # ❌ Slow!

# Should be:
result = "".join(items)  # ✅ Much faster
```

### 📝 Code Quality
- Missing docstrings
- High complexity functions
- Wildcard imports
- Improper exception handling
- And more!

---

## 📊 Example Output

```
================================================================================
CODE ANALYSIS REPORT
================================================================================
File: example.py

SUMMARY
Code Metrics:
  - Lines of Code: 50
  - Functions: 5
  - Valid Syntax: ✓

Issues Found:
  - Critical: 2
  - High: 1
  - Medium: 3

DETAILED ISSUES

Issue #1
Type: Security
Severity: CRITICAL
Line: 10
Description: Hardcoded secret detected
Suggestion: Use environment variables

[... more issues ...]

OPTIMIZATION SUGGESTIONS
  • Line 12: Use enumerate() instead of range(len())
  • Line 23: Consider using list comprehension
```

---

## 🛠️ Common Use Cases

### Use Case 1: Check Before Commit
```bash
# In your pre-commit hook
python cli.py changed_files.py --severity critical,high
if [ $? -ne 0 ]; then
    echo "Fix issues before committing!"
    exit 1
fi
```

### Use Case 2: Code Review Assistant
```python
from code_analyzer_system import analyze_code_file

result = analyze_code_file("pull_request.py")
critical_issues = [
    i for i in result["analysis_results"].issues
    if i.severity.value in ["critical", "high"]
]

if critical_issues:
    print("❌ Pull request has critical issues!")
    for issue in critical_issues:
        print(f"  Line {issue.line_number}: {issue.description}")
```

### Use Case 3: Continuous Monitoring
```bash
# In CI/CD pipeline
python cli.py src/ --recursive --format json > report.json

# Check results
python -c "
import json, sys
with open('report.json') as f:
    data = json.load(f)
    if data['summary']['total_issues'] > 0:
        print('Issues found!')
        sys.exit(1)
"
```

---

## 🎓 Learn More

### Next Steps:
1. **Read README.md** - Full documentation and architecture
2. **Check USAGE_GUIDE.md** - Comprehensive examples
3. **Review PROJECT_STRUCTURE.md** - Technical details
4. **Experiment!** - Try it on your code

### Want to Customize?
```python
# Check config.py for configuration options
from config import STRICT_CONFIG, PERMISSIVE_CONFIG

# Or create your own
from config import AnalyzerConfig

my_config = AnalyzerConfig(
    min_severity="high",
    check_hardcoded_secrets=True,
    max_cyclomatic_complexity=5
)
```

---

## 💡 Pro Tips

1. **Start with the demo** - `python quick_start.py`
2. **Test on example file** - See what it catches in `test_examples/buggy_code.py`
3. **Use the CLI for automation** - Perfect for scripts and CI/CD
4. **Customize for your needs** - Adjust config.py settings
5. **Integrate early** - The earlier you catch issues, the better

---

## 🆘 Having Issues?

### Problem: "No module named 'code_analyzer_system'"
**Solution:** Make sure you're in the correct directory:
```bash
cd code-analyzer-system
python quick_start.py
```

### Problem: Want to use LangGraph features
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Problem: Getting too many low-severity warnings
**Solution:** Filter by severity:
```bash
python cli.py script.py --severity critical,high
```

---

## 🚀 What's Next?

### Beginner Track:
1. ✅ Run `quick_start.py`
2. ✅ Analyze your own code
3. ✅ Read the reports
4. ✅ Fix the issues!

### Intermediate Track:
1. ✅ Use the CLI in your workflow
2. ✅ Customize configuration
3. ✅ Integrate with git hooks
4. ✅ Add to CI/CD

### Advanced Track:
1. ✅ Study the multi-agent architecture
2. ✅ Set up LangGraph integration
3. ✅ Create custom agents
4. ✅ Extend detection rules

---

## 📚 Documentation Quick Links

- **README.md** - Overview, architecture, features
- **USAGE_GUIDE.md** - Detailed examples and patterns
- **PROJECT_STRUCTURE.md** - Technical architecture
- **config.py** - Configuration options
- **langgraph_implementation.py** - LangGraph template

---

## 🎉 You're Ready!

You now have a powerful multi-agent code analyzer at your fingertips. 

**Quick command to get started:**
```bash
python quick_start.py
```

**Or dive right in:**
```bash
python cli.py your_code.py
```

Happy coding! 🚀

---

**Questions or Issues?**
- Check the documentation files
- Review the example code
- Experiment with the demo

**Built with ❤️ using LangGraph architecture**