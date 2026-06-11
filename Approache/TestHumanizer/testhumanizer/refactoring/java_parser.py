from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from tree_sitter import Language, Parser
import tree_sitter_java


@dataclass
class JavaExtraction:
    package_name: Optional[str]
    test_class_name: str
    test_class_fqdn: str
    fqdn_path: str
    static_part: str
    test_code: str
    full_code: str
    test_method_count: int
    helper_method_count: int

def _make_parser() -> Parser:
    parser = Parser()

    # Works with recent tree-sitter-java.
    language = Language(tree_sitter_java.language())
    parser.language = language

    return parser

# def _make_parser():
#     """
#     Build a Java Tree-sitter parser using tree-sitter-language-pack.

#     In this environment, get_parser("java") returns the language-pack Parser,
#     whose API is:
#       - parse(source: str)
#       - parse_bytes(source: bytes)

#     This avoids the dependency conflict between codebleu==0.7.0 and recent
#     tree-sitter-java wheels.
#     """
#     try:
#         return get_parser("java")
#     except Exception as e:
#         raise RuntimeError(
#             "Could not initialize Java parser from tree-sitter-language-pack. "
#             "Install with: pip install tree-sitter-language-pack"
#         ) from e


def read_text(path: str | Path) -> str:
    p = Path(path).expanduser().resolve()
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="latin-1")


def _node_type(node) -> str:
    if hasattr(node, "type"):
        value = node.type
        return value() if callable(value) else value

    if hasattr(node, "kind"):
        value = node.kind
        return value() if callable(value) else value

    raise AttributeError(f"Cannot get node type/kind from node: {node}")


def _node_start_byte(node) -> int:
    value = getattr(node, "start_byte")
    return value() if callable(value) else value


def _node_end_byte(node) -> int:
    value = getattr(node, "end_byte")
    return value() if callable(value) else value


def _node_start_point(node) -> tuple[int, int]:
    if hasattr(node, "start_point"):
        value = node.start_point
        point = value() if callable(value) else value
        if isinstance(point, tuple):
            return point
        if hasattr(point, "row") and hasattr(point, "column"):
            return int(point.row), int(point.column)

    if hasattr(node, "start_position"):
        point = node.start_position()
        if isinstance(point, tuple):
            return point
        if hasattr(point, "row") and hasattr(point, "column"):
            return int(point.row), int(point.column)

    raise AttributeError(f"Cannot get start point from node: {node}")


def _node_children(node) -> List:
    if hasattr(node, "children"):
        children = node.children
        return list(children() if callable(children) else children)

    if hasattr(node, "child_count") and hasattr(node, "child"):
        count = node.child_count()
        return [node.child(i) for i in range(count) if node.child(i) is not None]

    return []


def _root_node(tree):
    if hasattr(tree, "root_node"):
        value = tree.root_node
        return value() if callable(value) else value

    raise AttributeError(f"Cannot get root node from tree: {tree}")


def node_text(source: bytes, node) -> str:
    start = _node_start_byte(node)
    end = _node_end_byte(node)
    return source[start:end].decode("utf-8", errors="replace")


def line_start_byte(source: bytes, line_index_zero_based: int) -> int:
    if line_index_zero_based <= 0:
        return 0

    current_line = 0
    for i, b in enumerate(source):
        if b == ord("\n"):
            current_line += 1
            if current_line == line_index_zero_based:
                return i + 1

    return len(source)


def find_nodes_by_type(node, wanted_type: str) -> List:
    result = []

    def visit(n):
        if _node_type(n) == wanted_type:
            result.append(n)

        for child in _node_children(n):
            visit(child)

    visit(node)
    return result


def find_first_node_by_type(node, wanted_type: str):
    nodes = find_nodes_by_type(node, wanted_type)
    return nodes[0] if nodes else None


def extract_package_name(source: bytes, root) -> Optional[str]:
    package_node = find_first_node_by_type(root, "package_declaration")
    if package_node is None:
        return None

    text = node_text(source, package_node)
    match = re.search(r"package\s+([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)*)\s*;", text)
    if not match:
        return None

    return match.group(1)


def extract_class_name(source: bytes, class_node) -> str:
    for child in _node_children(class_node):
        if _node_type(child) == "identifier":
            return node_text(source, child)

    text = node_text(source, class_node)
    match = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", text)
    if match:
        return match.group(1)

    raise ValueError("Could not extract class name from class_declaration.")


def has_test_annotation(source: bytes, method_node) -> bool:
    prefix = source[
        _node_start_byte(method_node): min(_node_end_byte(method_node), _node_start_byte(method_node) + 500)
    ].decode("utf-8", errors="replace")

    return "@Test" in prefix


def find_class_body_node(class_node):
    for child in _node_children(class_node):
        if _node_type(child) == "class_body":
            return child
    return None


def extract_methods(source: bytes, class_node) -> Tuple[List, List]:
    """
    Return:
      test_methods, helper_methods

    helper_methods are method_declaration nodes in the test class body that are not @Test.
    """
    class_body = find_class_body_node(class_node)
    if class_body is None:
        return [], []

    methods = []

    for child in _node_children(class_body):
        child_type = _node_type(child)

        if child_type == "method_declaration":
            methods.append(child)

        # Avoid descending into nested classes/interfaces for now.
        elif child_type in {
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
            "record_declaration",
        }:
            continue

    test_methods = [m for m in methods if has_test_annotation(source, m)]
    helper_methods = [m for m in methods if not has_test_annotation(source, m)]

    return test_methods, helper_methods


def build_static_part(source: bytes, first_refactorable_node) -> str:
    """
    static_part = everything from file start up to first refactorable method/helper.

    This keeps:
      - package declaration
      - imports
      - EvoSuite runner imports
      - class annotations
      - class declaration
      - fields declared before first method, if any
    """
    cut_line = _node_start_point(first_refactorable_node)[0]
    cut_at_line_start = line_start_byte(source, cut_line)

    return source[:cut_at_line_start].decode("utf-8", errors="replace").rstrip()


def build_refactorable_code(source: bytes, nodes: List) -> str:
    if not nodes:
        return ""

    parts = []
    for node in sorted(nodes, key=_node_start_byte):
        parts.append(node_text(source, node).rstrip())

    return "\n\n".join(parts).strip()


def _parse_java_source(parser, full_code: str):
    """
    Handle both tree-sitter-language-pack parser APIs and py-tree-sitter parser APIs.
    """
    source_bytes = full_code.encode("utf-8", errors="replace")

    if hasattr(parser, "parse_bytes"):
        tree = parser.parse_bytes(source_bytes)
    else:
        tree = parser.parse(source_bytes)

    if tree is None:
        raise ValueError("Tree-sitter returned no parse tree.")

    return tree, source_bytes


def extract_java_test_parts(test_file: str | Path) -> JavaExtraction:
    test_file = Path(test_file).expanduser().resolve()
    full_code = read_text(test_file)

    parser = _make_parser()
    tree, source = _parse_java_source(parser, full_code)
    root = _root_node(tree)

    class_node = find_first_node_by_type(root, "class_declaration")
    if class_node is None:
        raise ValueError(f"No class_declaration found in {test_file}")

    package_name = extract_package_name(source, root)
    test_class_name = extract_class_name(source, class_node)

    if package_name:
        test_class_fqdn = f"{package_name}.{test_class_name}"
        fqdn_path = package_name.replace(".", "/")
    else:
        test_class_fqdn = test_class_name
        fqdn_path = ""

    test_methods, helper_methods = extract_methods(source, class_node)

    refactorable_nodes = sorted(test_methods + helper_methods, key=_node_start_byte)

    if not refactorable_nodes:
        raise ValueError(f"No refactorable method found in {test_file}")

    static_part = build_static_part(source, refactorable_nodes[0])
    test_code = build_refactorable_code(source, refactorable_nodes)

    return JavaExtraction(
        package_name=package_name,
        test_class_name=test_class_name,
        test_class_fqdn=test_class_fqdn,
        fqdn_path=fqdn_path,
        static_part=static_part,
        test_code=test_code,
        full_code=full_code,
        test_method_count=len(test_methods),
        helper_method_count=len(helper_methods),
    )




####################"""
# from __future__ import annotations

# import re
# from dataclasses import dataclass
# from pathlib import Path
# from typing import List, Optional, Tuple

# from tree_sitter import Language, Parser
# import tree_sitter_java


# @dataclass
# class JavaExtraction:
#     package_name: Optional[str]
#     test_class_name: str
#     test_class_fqdn: str
#     fqdn_path: str
#     static_part: str
#     test_code: str
#     full_code: str
#     test_method_count: int
#     helper_method_count: int


# def _make_parser() -> Parser:
#     parser = Parser()

#     # Works with recent tree-sitter-java.
#     language = Language(tree_sitter_java.language())
#     parser.language = language

#     return parser


# def read_text(path: str | Path) -> str:
#     p = Path(path).expanduser().resolve()
#     try:
#         return p.read_text(encoding="utf-8")
#     except UnicodeDecodeError:
#         return p.read_text(encoding="latin-1")


# def node_text(source: bytes, node) -> str:
#     return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


# def line_start_byte(source: bytes, line_index_zero_based: int) -> int:
#     if line_index_zero_based <= 0:
#         return 0

#     current_line = 0
#     for i, b in enumerate(source):
#         if b == ord("\n"):
#             current_line += 1
#             if current_line == line_index_zero_based:
#                 return i + 1

#     return len(source)


# def find_nodes_by_type(node, wanted_type: str) -> List:
#     result = []

#     def visit(n):
#         if n.type == wanted_type:
#             result.append(n)
#         for child in n.children:
#             visit(child)

#     visit(node)
#     return result


# def find_first_node_by_type(node, wanted_type: str):
#     nodes = find_nodes_by_type(node, wanted_type)
#     return nodes[0] if nodes else None


# def extract_package_name(source: bytes, root) -> Optional[str]:
#     package_node = find_first_node_by_type(root, "package_declaration")
#     if package_node is None:
#         return None

#     text = node_text(source, package_node)
#     match = re.search(r"package\s+([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)*)\s*;", text)
#     if not match:
#         return None

#     return match.group(1)


# def extract_class_name(source: bytes, class_node) -> str:
#     for child in class_node.children:
#         if child.type == "identifier":
#             return node_text(source, child)

#     text = node_text(source, class_node)
#     match = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", text)
#     if match:
#         return match.group(1)

#     raise ValueError("Could not extract class name from class_declaration.")


# def has_test_annotation(source: bytes, method_node) -> bool:
#     """
#     Detect JUnit @Test annotation among method modifiers.
#     """
#     method_text_prefix = source[method_node.start_byte:method_node.start_byte + 400].decode(
#         "utf-8", errors="replace"
#     )
#     return "@Test" in method_text_prefix


# def find_class_body_node(class_node):
#     for child in class_node.children:
#         if child.type == "class_body":
#             return child
#     return None


# def extract_methods(source: bytes, class_node) -> Tuple[List, List]:
#     """
#     Return:
#       test_methods, helper_methods

#     helper_methods are method_declaration nodes in the test class body that are not @Test.
#     """
#     class_body = find_class_body_node(class_node)
#     if class_body is None:
#         return [], []

#     methods = []

#     def visit_direct_body(n):
#         # We collect method declarations inside the class body.
#         # This ignores methods of nested classes if any are nested deeper.
#         for child in n.children:
#             if child.type == "method_declaration":
#                 methods.append(child)
#             elif child.type in {"field_declaration", "{", "}"}:
#                 continue
#             elif child.type.endswith("declaration"):
#                 # Avoid descending into nested classes/interfaces.
#                 continue
#             else:
#                 # Some tree-sitter versions wrap declarations differently.
#                 if child.type not in {"class_body"}:
#                     continue

#     visit_direct_body(class_body)

#     test_methods = [m for m in methods if has_test_annotation(source, m)]
#     helper_methods = [m for m in methods if not has_test_annotation(source, m)]

#     return test_methods, helper_methods


# def build_static_part(source: bytes, class_node, first_refactorable_node) -> str:
#     """
#     static_part = everything from file start up to first refactorable method/helper.

#     This keeps:
#       - package declaration
#       - imports
#       - EvoSuite runner imports
#       - class annotations
#       - class declaration
#       - fields declared before first method, if any
#     """
#     cut_byte = first_refactorable_node.start_byte
#     cut_line = first_refactorable_node.start_point[0]
#     cut_at_line_start = line_start_byte(source, cut_line)

#     static = source[:cut_at_line_start].decode("utf-8", errors="replace").rstrip()

#     return static


# def build_refactorable_code(source: bytes, nodes: List) -> str:
#     if not nodes:
#         return ""

#     parts = []
#     for node in sorted(nodes, key=lambda n: n.start_byte):
#         parts.append(node_text(source, node).rstrip())

#     return "\n\n".join(parts).strip()


# def extract_java_test_parts(test_file: str | Path) -> JavaExtraction:
#     test_file = Path(test_file).expanduser().resolve()
#     full_code = read_text(test_file)
#     source = full_code.encode("utf-8", errors="replace")

#     parser = _make_parser()
#     tree = parser.parse(source)
#     root = tree.root_node

#     class_node = find_first_node_by_type(root, "class_declaration")
#     if class_node is None:
#         raise ValueError(f"No class_declaration found in {test_file}")

#     package_name = extract_package_name(source, root)
#     test_class_name = extract_class_name(source, class_node)

#     if package_name:
#         test_class_fqdn = f"{package_name}.{test_class_name}"
#         fqdn_path = package_name.replace(".", "/")
#     else:
#         test_class_fqdn = test_class_name
#         fqdn_path = ""

#     test_methods, helper_methods = extract_methods(source, class_node)

#     refactorable_nodes = sorted(test_methods + helper_methods, key=lambda n: n.start_byte)

#     if not refactorable_nodes:
#         raise ValueError(f"No refactorable method found in {test_file}")

#     static_part = build_static_part(source, class_node, refactorable_nodes[0])
#     test_code = build_refactorable_code(source, refactorable_nodes)

#     # Add closing brace information to the LLM implicitly through static part constraints.
#     # The extracted code is expected to be regenerated as a complete class by the prompt.

#     return JavaExtraction(
#         package_name=package_name,
#         test_class_name=test_class_name,
#         test_class_fqdn=test_class_fqdn,
#         fqdn_path=fqdn_path,
#         static_part=static_part,
#         test_code=test_code,
#         full_code=full_code,
#         test_method_count=len(test_methods),
#         helper_method_count=len(helper_methods),
#     )
