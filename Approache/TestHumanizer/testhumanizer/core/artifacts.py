from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class TargetClass:
    dataset: str
    project: str
    class_name: str
    source_path: Path
    bug_id: Optional[str] = None
    classpath: Optional[str] = None
    test_class_fqdn: Optional[str] = None
    class_files_dir: Optional[str] = None
    source_files_dir: Optional[str] = None

@dataclass
class GeneratedTestSuite:
    target: TargetClass
    testsuite_id: str
    test_file: Path
    scaffolding_file: Optional[Path]
    output_dir: Path
    generator: str = "evosuite"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassSummary:
    target: TargetClass
    model: str
    attempt: int
    summary: str
    side_score: Optional[float] = None


@dataclass
class RefactoringContext:
    scenario: str
    static_part: str
    test_code: str
    source_code: Optional[str] = None
    class_summary: Optional[str] = None


@dataclass
class RefactoringResult:
    target: TargetClass
    testsuite_id: str
    scenario: str
    model: str
    attempt: int
    raw_output: str
    extracted_code: Optional[str]
    output_dir: Path
    syntax_valid: Optional[bool] = None
    compiles: Optional[bool] = None
    junit_passes: Optional[bool] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
