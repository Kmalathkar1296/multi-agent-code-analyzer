"""
Configuration for Code Analyzer System
Customize agent behavior and detection rules
"""

from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class AnalyzerConfig:
    """Configuration for the code analyzer"""
    
    # Enabled agents
    enabled_agents: Set[str] = None
    
    # Severity thresholds
    min_severity: str = "info"  # info, low, medium, high, critical
    
    # Complexity thresholds
    max_cyclomatic_complexity: int = 10
    max_function_lines: int = 50
    max_class_lines: int = 300
    
    # Performance settings
    check_string_concatenation: bool = True
    check_list_comprehension: bool = True
    check_global_lookups: bool = True
    
    # Security settings
    check_hardcoded_secrets: bool = True
    check_sql_injection: bool = True
    check_eval_exec: bool = True
    check_insecure_random: bool = True
    
    # Code style settings
    require_docstrings: bool = True
    check_wildcard_imports: bool = True
    max_line_length: int = 100
    
    # Exception handling
    allow_bare_except: bool = False
    allow_empty_except: bool = False
    
    # File patterns to ignore
    ignore_patterns: List[str] = None
    
    # Custom patterns to detect
    custom_patterns: Dict[str, str] = None
    
    def __post_init__(self):
        if self.enabled_agents is None:
            self.enabled_agents = {
                "parser",
                "bug_detector", 
                "performance",
                "security",
                "reporter"
            }
        
        if self.ignore_patterns is None:
            self.ignore_patterns = [
                "*/test_*",
                "*/tests/*",
                "*/__pycache__/*",
                "*.pyc",
                "*/.venv/*",
                "*/venv/*",
            ]
        
        if self.custom_patterns is None:
            self.custom_patterns = {}


# Default configuration
DEFAULT_CONFIG = AnalyzerConfig()

# Strict configuration (for production code)
STRICT_CONFIG = AnalyzerConfig(
    min_severity="medium",
    max_cyclomatic_complexity=5,
    max_function_lines=30,
    allow_bare_except=False,
    allow_empty_except=False,
    require_docstrings=True,
)

# Permissive configuration (for prototyping)
PERMISSIVE_CONFIG = AnalyzerConfig(
    min_severity="high",
    max_cyclomatic_complexity=20,
    max_function_lines=100,
    require_docstrings=False,
    check_string_concatenation=False,
)

# Security-focused configuration
SECURITY_FOCUSED_CONFIG = AnalyzerConfig(
    enabled_agents={"security", "reporter"},
    min_severity="low",
    check_hardcoded_secrets=True,
    check_sql_injection=True,
    check_eval_exec=True,
    check_insecure_random=True,
)

# Performance-focused configuration
PERFORMANCE_FOCUSED_CONFIG = AnalyzerConfig(
    enabled_agents={"performance", "reporter"},
    min_severity="medium",
    check_string_concatenation=True,
    check_list_comprehension=True,
    check_global_lookups=True,
    max_cyclomatic_complexity=8,
)


def load_config(config_name: str = "default") -> AnalyzerConfig:
    """Load a predefined configuration"""
    configs = {
        "default": DEFAULT_CONFIG,
        "strict": STRICT_CONFIG,
        "permissive": PERMISSIVE_CONFIG,
        "security": SECURITY_FOCUSED_CONFIG,
        "performance": PERFORMANCE_FOCUSED_CONFIG,
    }
    
    return configs.get(config_name, DEFAULT_CONFIG)


# Example: Custom configuration
"""
custom_config = AnalyzerConfig(
    enabled_agents={"parser", "security", "reporter"},
    min_severity="high",
    custom_patterns={
        "todo_comments": r"#\s*TODO:",
        "deprecated_functions": r"deprecated_func\(",
    }
)
"""