"""安全读取 glo.env，屏蔽敏感值，保留注释和非敏感值。"""
import sys
import re
from pathlib import Path

SENSITIVE_PATTERNS = re.compile(
    r'(KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|PRIVATE)', re.IGNORECASE
)

GLO_ENV = Path.home() / '.claude' / 'glo.env'


def mask_read(filepath: Path = GLO_ENV):
    if not filepath.exists():
        print(f"[ERROR] 文件不存在: {filepath}", file=sys.stderr)
        sys.exit(1)

    for line in filepath.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()

        # 空行或注释原样输出
        if not stripped or stripped.startswith('#'):
            print(line)
            continue

        # 尝试解析 KEY=VALUE
        if '=' in stripped:
            key, _, value = stripped.partition('=')
            key = key.strip()
            value = value.strip()

            if SENSITIVE_PATTERNS.search(key):
                print(f"{key}=***")
            else:
                print(f"{key}={value}")
        else:
            # 非键值对行（兼容旧格式残留）
            print(f"# {line}")


if __name__ == '__main__':
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else GLO_ENV
    mask_read(path)
