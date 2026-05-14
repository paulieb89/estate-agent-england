"""Format integrity checks — prevents minified/collapsed file commits.

Checks that .py, .md, .toml, and .json files are not minified (single-line or
near-empty). Also validates that JSON and TOML files parse correctly, that
.mcp.json points to the expected hosted MCP server, and that every MCP tool
name referenced in a skill exists in the frozen property-shared contract.
"""
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent

# Directories to scan
PY_FILES = list(PLUGIN_ROOT.glob("scripts/*.py"))
MD_FILES = (
    list(PLUGIN_ROOT.glob("skills/*/SKILL.md"))
    + list(PLUGIN_ROOT.glob("agents/*.md"))
    + list(PLUGIN_ROOT.glob("references/*.md"))
)
# Only plugin component files require YAML frontmatter
FRONTMATTER_MD_FILES = (
    list(PLUGIN_ROOT.glob("skills/*/SKILL.md"))
    + list(PLUGIN_ROOT.glob("agents/*.md"))
)
JSON_FILES = (
    list(PLUGIN_ROOT.glob(".claude-plugin/*.json"))
    + list(PLUGIN_ROOT.glob("fixtures/*.json"))
    + [PLUGIN_ROOT / ".mcp.json"]
)
TOML_FILES = [PLUGIN_ROOT / "pyproject.toml"]


# ---------------------------------------------------------------------------
# Python files
# ---------------------------------------------------------------------------

def test_python_files_not_minified():
    for path in PY_FILES:
        lines = path.read_text().splitlines()
        assert len(lines) >= 10, (
            f"{path.relative_to(PLUGIN_ROOT)} appears minified or near-empty ({len(lines)} lines)"
        )


def test_python_files_parse():
    import py_compile
    for path in PY_FILES:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            raise AssertionError(f"{path.name} does not compile: {exc}") from exc


# ---------------------------------------------------------------------------
# Markdown files
# ---------------------------------------------------------------------------

def test_markdown_files_not_minified():
    for path in MD_FILES:
        lines = path.read_text().splitlines()
        assert len(lines) >= 5, (
            f"{path.relative_to(PLUGIN_ROOT)} appears minified or near-empty ({len(lines)} lines)"
        )


def test_markdown_files_have_frontmatter():
    for path in FRONTMATTER_MD_FILES:
        content = path.read_text()
        assert content.startswith("---\n"), (
            f"{path.relative_to(PLUGIN_ROOT)} is missing YAML frontmatter (does not start with ---)"
        )
        end = content.index("---\n", 4)
        frontmatter = content[4:end]
        assert "description:" in frontmatter, (
            f"{path.relative_to(PLUGIN_ROOT)} frontmatter missing 'description:' field"
        )


# ---------------------------------------------------------------------------
# JSON files
# ---------------------------------------------------------------------------

def test_json_files_parse():
    for path in JSON_FILES:
        if not path.exists():
            continue
        try:
            json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{path.name} is not valid JSON: {exc}") from exc


def test_json_files_not_minified():
    for path in JSON_FILES:
        if not path.exists():
            continue
        lines = path.read_text().splitlines()
        assert len(lines) >= 3, (
            f"{path.relative_to(PLUGIN_ROOT)} appears minified or collapsed ({len(lines)} lines)"
        )


# ---------------------------------------------------------------------------
# TOML files
# ---------------------------------------------------------------------------

def test_toml_files_parse():
    for path in TOML_FILES:
        try:
            tomllib.loads(path.read_text())
        except tomllib.TOMLDecodeError as exc:
            raise AssertionError(f"{path.name} is not valid TOML: {exc}") from exc


def test_toml_files_not_minified():
    for path in TOML_FILES:
        lines = path.read_text().splitlines()
        assert len(lines) >= 5, (
            f"{path.relative_to(PLUGIN_ROOT)} appears minified or near-empty ({len(lines)} lines)"
        )


# ---------------------------------------------------------------------------
# MCP contract
# ---------------------------------------------------------------------------

def test_mcp_config_points_to_property_shared():
    config = json.loads((PLUGIN_ROOT / ".mcp.json").read_text())
    server = config["mcpServers"]["property-shared"]
    assert server["type"] == "http"
    assert server["url"].startswith("https://property-shared.fly.dev/")


# Matches tool invocations — name followed by `(` — to avoid false positives
# from parameter names like `property_type` that share the prefix.
_MCP_TOOL_CALL_PATTERN = re.compile(
    r"\b((?:property|ppd|rental|rightmove)_[a-z_]+)\s*\("
)


def test_skill_mcp_tools_in_contract():
    contract_path = PLUGIN_ROOT / "references" / "property-shared-tools.json"
    contract_tools = set(json.loads(contract_path.read_text()))
    for path in PLUGIN_ROOT.glob("skills/*/SKILL.md"):
        content = path.read_text()
        for match in _MCP_TOOL_CALL_PATTERN.finditer(content):
            tool_name = match.group(1)
            assert tool_name in contract_tools, (
                f"{path.parent.name}/SKILL.md references MCP tool '{tool_name}' "
                f"not in references/property-shared-tools.json"
            )
