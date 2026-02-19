"""盲迁移：从 glo.env 复制指定键值对到目标 .env，AI 不接触值。"""
import sys
import argparse
from pathlib import Path

GLO_ENV = Path.home() / '.claude' / 'glo.env'


def parse_env(filepath: Path) -> dict:
    """解析 .env 文件，返回 {KEY: VALUE} 字典。"""
    entries = {}
    if not filepath.exists():
        return entries
    for line in filepath.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if '=' in stripped:
            key, _, value = stripped.partition('=')
            entries[key.strip()] = value.strip()
    return entries


def check_gitignore(target_dir: Path):
    """检查目标目录的 .gitignore 是否包含 .env。"""
    gitignore = target_dir / '.gitignore'
    if not gitignore.exists():
        print("[WARN] 目标目录没有 .gitignore，建议添加 .env 到其中")
        return
    content = gitignore.read_text(encoding='utf-8')
    if '.env' not in content:
        print("[WARN] .gitignore 中未包含 .env，建议添加以防密钥泄露")


def migrate(keys: list[str], target: Path, source: Path = GLO_ENV):
    if not source.exists():
        print(f"[ERROR] 源文件不存在: {source}", file=sys.stderr)
        sys.exit(1)

    src_entries = parse_env(source)
    tgt_entries = parse_env(target)

    migrated = []
    skipped = []
    not_found = []

    for key in keys:
        if key not in src_entries:
            not_found.append(key)
        elif key in tgt_entries:
            skipped.append(key)
        else:
            migrated.append(key)

    # 追加到目标文件
    if migrated:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, 'a', encoding='utf-8') as f:
            if target.exists() and target.stat().st_size > 0:
                f.write('\n')
            for key in migrated:
                f.write(f"{key}={src_entries[key]}\n")

    # 检查 .gitignore
    check_gitignore(target.parent)

    # 输出摘要（不含值）
    print(f"[OK] 已迁移 {len(migrated)} 个键: {', '.join(migrated)}" if migrated else "[INFO] 无新键需要迁移")
    if skipped:
        print(f"[SKIP] 已存在，跳过: {', '.join(skipped)}")
    if not_found:
        print(f"[WARN] 源文件中未找到: {', '.join(not_found)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='盲迁移密钥到项目 .env')
    parser.add_argument('--keys', required=True, help='逗号分隔的键名列表')
    parser.add_argument('--target', required=True, help='目标 .env 文件路径')
    parser.add_argument('--source', default=str(GLO_ENV), help='源 .env 文件路径')
    args = parser.parse_args()

    key_list = [k.strip() for k in args.keys.split(',')]
    migrate(key_list, Path(args.target), Path(args.source))
