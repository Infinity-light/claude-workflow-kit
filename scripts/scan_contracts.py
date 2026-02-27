#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scan_contracts.py - 契约扫描脚本

扫描项目中所有代码文件的 YAML frontmatter 契约块，生成进度报告。

用法：python -X utf8 .claude/scripts/scan_contracts.py <project_root>
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".vue",
    ".java", ".go", ".rs", ".rb", ".kt", ".swift",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".php",
}

EXCLUDE_DIRS = {
    "node_modules", ".git", "__pycache__", ".claude",
    "dist", "build", ".next", ".nuxt", "venv", ".venv",
    "target", "vendor", ".idea", ".vscode",
}

VALID_STATUSES = {"PENDING", "IMPLEMENTED", "VERIFIED"}

STATUS_EMOJI = {
    "PENDING": "⬜",
    "IMPLEMENTED": "🔨",
    "VERIFIED": "✅",
}


# ---------------------------------------------------------------------------
# 契约解析
# ---------------------------------------------------------------------------

def strip_comment_prefix(line: str) -> str:
    """去除行首的注释前缀，如 ' * ', ' # ', '// ' 等。"""
    # 匹配 /** ... */ 风格中的 " * " 前缀
    m = re.match(r"^\s*\*\s?", line)
    if m:
        return line[m.end():]
    # 匹配 # 注释前缀（Python docstring 内部通常没有 #，但保留兼容）
    m = re.match(r"^\s*#\s?", line)
    if m:
        return line[m.end():]
    # 匹配 // 注释前缀
    m = re.match(r"^\s*//\s?", line)
    if m:
        return line[m.end():]
    return line


def extract_contract_block(content: str) -> str | None:
    """
    从文件内容中提取 --- 和 --- 之间的契约块原始文本。
    返回去除注释前缀后的纯文本，或 None。
    """
    # 匹配多行注释内部或文档字符串内部的 --- 块
    # 策略：逐行扫描，找到第一对 ---
    lines = content.splitlines()
    inside = False
    block_lines: list[str] = []

    for raw_line in lines:
        stripped = strip_comment_prefix(raw_line).rstrip()
        # 也处理原始行本身就是 --- 的情况（如 Python docstring）
        raw_stripped = raw_line.strip().lstrip("#").lstrip("/").lstrip("*").strip()

        if stripped == "---" or raw_stripped == "---":
            if inside:
                # 找到结束标记
                return "\n".join(block_lines)
            else:
                inside = True
                block_lines = []
                continue

        if inside:
            block_lines.append(stripped)

    return None


def parse_contract_yaml(text: str) -> dict:
    """
    手动解析简单 YAML 格式的契约字段。
    支持的字段：role, depends, status, functions
    """
    result: dict = {
        "role": "",
        "depends": [],
        "status": "PENDING",
        "functions": [],
    }

    lines = text.splitlines()
    current_key = None
    current_list: list[str] = []

    for line in lines:
        # 顶层 key: value
        m = re.match(r"^(\w+):\s*(.*)", line)
        if m:
            # 先保存上一个列表型 key
            if current_key == "functions" and current_list:
                result["functions"] = current_list
                current_list = []

            key = m.group(1)
            value = m.group(2).strip()

            if key == "role":
                result["role"] = value
                current_key = "role"
            elif key == "depends":
                result["depends"] = _parse_inline_list(value)
                current_key = "depends"
            elif key == "status":
                value_upper = value.upper()
                if value_upper in VALID_STATUSES:
                    result["status"] = value_upper
                current_key = "status"
            elif key == "functions":
                current_key = "functions"
                current_list = []
            else:
                current_key = key
            continue

        # 列表项（以 - 开头）
        m_list = re.match(r"^\s+-\s+(.*)", line)
        if m_list and current_key == "functions":
            current_list.append(m_list.group(1).strip())
            continue

        # 续行（函数描述等缩进行）
        if current_key == "functions" and line.strip() and current_list:
            current_list[-1] += " " + line.strip()

    # 收尾
    if current_key == "functions" and current_list:
        result["functions"] = current_list

    return result


def _parse_inline_list(value: str) -> list[str]:
    """解析 [a, b, c] 格式的内联列表。"""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1]
        return [item.strip() for item in inner.split(",") if item.strip()]
    if value:
        return [value]
    return []


# ---------------------------------------------------------------------------
# 文件扫描
# ---------------------------------------------------------------------------

def collect_code_files(root: Path) -> list[Path]:
    """递归收集项目中所有代码文件，排除特定目录。"""
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # 原地修改 dirnames 以跳过排除目录
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDE_DIRS and not d.startswith(".")
        ]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix.lower() in CODE_EXTENSIONS:
                files.append(fpath)
    files.sort()
    return files


def scan_file(fpath: Path) -> dict | None:
    """扫描单个文件，返回契约信息字典或 None。"""
    try:
        content = fpath.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None

    block = extract_contract_block(content)
    if block is None:
        return None

    contract = parse_contract_yaml(block)
    contract["file"] = fpath
    return contract


def scan_project(root: Path) -> list[dict]:
    """扫描整个项目，返回所有带契约的文件信息列表。"""
    files = collect_code_files(root)
    results: list[dict] = []
    for fpath in files:
        info = scan_file(fpath)
        if info is not None:
            results.append(info)
    return results


# ---------------------------------------------------------------------------
# 依赖检查
# ---------------------------------------------------------------------------

def check_dependencies(contracts: list[dict], root: Path) -> list[dict]:
    """
    检查每个契约的依赖是否满足（依赖文件已 VERIFIED）。
    为每个契约添加 deps_met (bool) 和 executable (bool) 字段。
    """
    # 建立 相对路径 -> status 的映射
    status_map: dict[str, str] = {}
    for c in contracts:
        rel = str(c["file"].relative_to(root)).replace("\\", "/")
        status_map[rel] = c["status"]

    for c in contracts:
        depends = c["depends"]
        if not depends:
            c["deps_met"] = True
        else:
            c["deps_met"] = all(
                status_map.get(dep.replace("\\", "/")) == "VERIFIED"
                for dep in depends
            )

        # 可执行 = PENDING 且依赖全部 VERIFIED
        # 或 IMPLEMENTED 且可以进行验证
        c["executable"] = (
            (c["status"] == "PENDING" and c["deps_met"])
            or (c["status"] == "IMPLEMENTED")
        )

    return contracts


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------

def generate_progress_md(contracts: list[dict], root: Path) -> str:
    """生成 progress.md 的内容。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(contracts)
    verified = sum(1 for c in contracts if c["status"] == "VERIFIED")
    implemented = sum(1 for c in contracts if c["status"] == "IMPLEMENTED")
    pending = sum(1 for c in contracts if c["status"] == "PENDING")

    lines: list[str] = []
    lines.append("# 项目进度（自动生成，勿手动编辑）")
    lines.append(f"最后扫描: {now}")
    lines.append("")
    lines.append("## 总览")
    lines.append(
        f"总文件: {total} | "
        f"✅ VERIFIED: {verified} | "
        f"🔨 IMPLEMENTED: {implemented} | "
        f"⬜ PENDING: {pending}"
    )
    lines.append("")

    # 文件状态表
    lines.append("## 文件状态")
    lines.append("| 文件 | 角色 | 状态 | 依赖满足 | 可执行 |")
    lines.append("|------|------|------|---------|--------|")

    for c in contracts:
        rel = str(c["file"].relative_to(root)).replace("\\", "/")
        role = c["role"] or "-"
        emoji = STATUS_EMOJI.get(c["status"], "❓")
        status_str = f"{emoji} {c['status']}"
        deps = "✅" if c["deps_met"] else "❌"
        exe = "✅" if c["executable"] else "-"
        lines.append(f"| {rel} | {role} | {status_str} | {deps} | {exe} |")

    lines.append("")

    # 下一步可执行
    lines.append("## 下一步可执行")
    lines.append("")

    actionable_pending = [
        c for c in contracts
        if c["status"] == "PENDING" and c["deps_met"]
    ]
    actionable_impl = [
        c for c in contracts
        if c["status"] == "IMPLEMENTED"
    ]

    if actionable_pending:
        lines.append("### 可开始实现（PENDING，依赖已满足）")
        for c in actionable_pending:
            rel = str(c["file"].relative_to(root)).replace("\\", "/")
            lines.append(f"- `{rel}` — {c['role']}")
        lines.append("")

    if actionable_impl:
        lines.append("### 可进行验证（IMPLEMENTED，待验证）")
        for c in actionable_impl:
            rel = str(c["file"].relative_to(root)).replace("\\", "/")
            lines.append(f"- `{rel}` — {c['role']}")
        lines.append("")

    if not actionable_pending and not actionable_impl:
        if verified == total and total > 0:
            lines.append("所有文件已 VERIFIED，项目完成！")
        elif total == 0:
            lines.append("未发现任何契约块。")
        else:
            lines.append("当前没有可直接执行的文件（可能存在循环依赖或依赖未满足）。")
        lines.append("")

    return "\n".join(lines)


def print_summary(contracts: list[dict], root: Path) -> None:
    """在控制台输出扫描摘要。"""
    total = len(contracts)
    verified = sum(1 for c in contracts if c["status"] == "VERIFIED")
    implemented = sum(1 for c in contracts if c["status"] == "IMPLEMENTED")
    pending = sum(1 for c in contracts if c["status"] == "PENDING")

    print()
    print("=" * 60)
    print("  契约扫描报告")
    print("=" * 60)
    print(f"  扫描目录: {root}")
    print(f"  发现契约: {total} 个文件")
    print()
    print(f"  ✅ VERIFIED:    {verified}")
    print(f"  🔨 IMPLEMENTED: {implemented}")
    print(f"  ⬜ PENDING:     {pending}")
    print()

    if total > 0:
        pct = verified / total * 100
        bar_len = 30
        filled = int(bar_len * verified / total)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  进度: [{bar}] {pct:.1f}%")
        print()

    # 列出可执行项
    actionable = [
        c for c in contracts
        if (c["status"] == "PENDING" and c["deps_met"])
        or c["status"] == "IMPLEMENTED"
    ]
    if actionable:
        print("  下一步可执行:")
        for c in actionable:
            rel = str(c["file"].relative_to(root)).replace("\\", "/")
            tag = "待实现" if c["status"] == "PENDING" else "待验证"
            print(f"    → [{tag}] {rel}")
        print()

    print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main() -> None:
    """脚本主入口。"""
    if len(sys.argv) < 2:
        print("用法: python -X utf8 .claude/scripts/scan_contracts.py <project_root>")
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"错误: 目录不存在 — {root}")
        sys.exit(1)

    # 扫描
    contracts = scan_project(root)

    # 依赖检查
    contracts = check_dependencies(contracts, root)

    # 生成进度文件
    claude_dir = root / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    progress_path = claude_dir / "progress.md"

    md_content = generate_progress_md(contracts, root)
    progress_path.write_text(md_content, encoding="utf-8")

    # 控制台输出
    print_summary(contracts, root)
    print(f"  进度文件已写入: {progress_path}")
    print()


if __name__ == "__main__":
    main()
