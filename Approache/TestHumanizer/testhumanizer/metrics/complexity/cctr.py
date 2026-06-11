from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tree_sitter import Language, Parser
import tree_sitter_java


def _make_parser() -> Parser:
    parser = Parser()
    language = Language(tree_sitter_java.language())
    parser.language = language
    return parser


@dataclass
class CCTRResult:
    ok: bool
    complexity: Optional[int]
    error: str = ""


class CognitiveComplexityCalculator:
    def __init__(self, code: str, method_name: str | None = None) -> None:
        self.code = code.encode("utf-8", errors="replace")
        self.method_name = method_name
        self.complexity = 0
        self.nest_level = 0
        self.parser = _make_parser()

    def compute_complexity(self) -> int:
        tree = self.parser.parse(self.code)
        root_node = tree.root_node
        self._analyze_node(root_node)
        return self.complexity

    def _analyze_node(self, node) -> None:
        for child in node.children:
            child_text = self.code[child.start_byte:child.end_byte].decode(
                "utf-8",
                errors="replace",
            )

            if child.type in {
                "if_statement",
                "for_statement",
                "enhanced_for_statement",
                "while_statement",
                "do_statement",
                "switch_expression",
                "switch_statement",
            }:
                self.complexity += 1 + self.nest_level
                self.nest_level += 1
                self._analyze_node(child)
                self.nest_level -= 1

            elif child.type == "catch_clause":
                self.complexity += 1 + self.nest_level
                self.nest_level += 1
                self._analyze_node(child)
                self.nest_level -= 1

            elif child.type == "annotation":
                if "@ParameterizedTest" in child_text:
                    self.complexity += 2
                elif "@Test" in child_text:
                    self.complexity += 1
                elif "@BeforeEach" in child_text or "@AfterEach" in child_text:
                    self.complexity += 1
                elif "@Before" in child_text or "@After" in child_text:
                    self.complexity += 1

            elif child.type == "expression_statement":
                if "assert" in child_text:
                    self.complexity += 1
                elif "throw" in child_text:
                    self.complexity += 1
                self._analyze_node(child)

            elif child.type == "throw_statement":
                self.complexity += 1
                self._analyze_node(child)

            elif child.type == "method_invocation":
                self.complexity += child_text.count(".")
                if self._is_recursive_call(child):
                    self.complexity += 2
                self._analyze_node(child)

            elif child.type in {
                "binary_expression",
                "ternary_expression",
                "lambda_expression",
            }:
                if "&&" in child_text or "||" in child_text:
                    self.complexity += 1
                if "?" in child_text and ":" in child_text:
                    self.complexity += 1
                self._analyze_node(child)

            else:
                self._analyze_node(child)

    def _is_recursive_call(self, node) -> bool:
        if self.method_name is None:
            return False

        node_text = self.code[node.start_byte:node.end_byte].decode(
            "utf-8",
            errors="replace",
        )

        invoked_method_name = node_text.split("(", 1)[0].strip()
        invoked_method_name = invoked_method_name.split(".")[-1].strip()

        return invoked_method_name == self.method_name


def analyze_java_file(java_file_path: str | Path) -> CCTRResult:
    java_file = Path(java_file_path).expanduser().resolve()

    if not java_file.exists():
        return CCTRResult(
            ok=False,
            complexity=None,
            error=f"Java file not found: {java_file}",
        )

    try:
        code = java_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        code = java_file.read_text(encoding="latin-1")

    try:
        calculator = CognitiveComplexityCalculator(code)
        complexity = calculator.compute_complexity()

        return CCTRResult(
            ok=True,
            complexity=complexity,
            error="",
        )

    except Exception as e:
        return CCTRResult(
            ok=False,
            complexity=None,
            error=f"{type(e).__name__}: {e}",
        )
