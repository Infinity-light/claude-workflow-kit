"""连通测试：从本地 .env 加载 key，测试 API 连通性，不暴露密钥值。"""
import sys
import argparse
import urllib.request
import urllib.error
import json
from pathlib import Path


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


def find_base_url(entries: dict, api_key_name: str) -> str | None:
    """根据 API_KEY 键名推断对应的 BASE_URL 键名。"""
    # DEEPSEEK_API_KEY -> DEEPSEEK_BASE_URL
    prefix = api_key_name.replace('_API_KEY', '').replace('_KEY', '').replace('_SECRET', '')
    candidates = [f"{prefix}_BASE_URL", f"{prefix}_ENDPOINT", f"{prefix}_URL"]
    for c in candidates:
        if c in entries:
            return entries[c]
    return None


def test_openai_compatible(base_url: str, api_key: str, key_name: str):
    """测试 OpenAI 兼容 API（/models 端点）。"""
    url = f"{base_url.rstrip('/')}/models"
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            models = data.get('data', [])
            model_ids = [m.get('id', '?') for m in models[:10]]
            suffix = f" (+{len(models)-10} more)" if len(models) > 10 else ""
            print(f"  {key_name}: OK (models: {', '.join(model_ids)}{suffix})")
    except urllib.error.HTTPError as e:
        print(f"  {key_name}: FAIL ({e.code} {e.reason})")
    except urllib.error.URLError as e:
        print(f"  {key_name}: FAIL (网络错误: {e.reason})")
    except TimeoutError:
        print(f"  {key_name}: TIMEOUT (10s)")
    except Exception as e:
        print(f"  {key_name}: FAIL ({type(e).__name__}: {e})")


def test_generic_url(url: str, key_name: str):
    """测试普通 HTTP URL 连通性。"""
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"  {key_name}: OK ({resp.status})")
    except urllib.error.HTTPError as e:
        print(f"  {key_name}: FAIL ({e.code} {e.reason})")
    except urllib.error.URLError as e:
        print(f"  {key_name}: FAIL (网络错误: {e.reason})")
    except TimeoutError:
        print(f"  {key_name}: TIMEOUT (10s)")


def ping_all(env_path: Path, filter_keys: list[str] | None = None):
    entries = parse_env(env_path)
    if not entries:
        print(f"[ERROR] .env 文件为空或不存在: {env_path}")
        sys.exit(1)

    import re
    sensitive = re.compile(r'(API_KEY|KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)', re.I)

    # 找出所有 API key 类的键
    api_keys = {k: v for k, v in entries.items() if sensitive.search(k)}
    if filter_keys:
        api_keys = {k: v for k, v in api_keys.items() if k in filter_keys}

    if not api_keys:
        print("[INFO] 未找到需要测试的 API 密钥")
        return

    print(f"测试 {len(api_keys)} 个密钥连通性...\n")

    for key_name, key_value in api_keys.items():
        base_url = find_base_url(entries, key_name)
        if base_url and ('api.' in base_url or 'openai' in base_url.lower()):
            test_openai_compatible(base_url, key_value, key_name)
        elif base_url:
            test_generic_url(base_url, key_name)
        else:
            print(f"  {key_name}: SKIP (未找到对应的 BASE_URL)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='测试 API 密钥连通性')
    parser.add_argument('--env', required=True, help='本地 .env 文件路径')
    parser.add_argument('--keys', default=None, help='逗号分隔的键名列表（可选，默认测试所有）')
    args = parser.parse_args()

    filter_keys = [k.strip() for k in args.keys.split(',')] if args.keys else None
    ping_all(Path(args.env), filter_keys)
