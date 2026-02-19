# Python开发模式

> 供Subagent执行Python开发任务时参考

## 代码风格

### PEP 8规范
- 缩进：4个空格
- 行长：最大79字符
- 命名：snake_case（变量/函数），PascalCase（类）

### 类型注解
```python
def greet(name: str) -> str:
    return f"Hello, {name}"

def process(items: list[int]) -> dict[str, int]:
    return {"sum": sum(items), "count": len(items)}
```

---

## 常用模式

### 上下文管理器
```python
# 文件操作
with open("file.txt", "r") as f:
    content = f.read()

# 自定义上下文管理器
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    yield
    print(f"Elapsed: {time.time() - start:.2f}s")
```

### 生成器
```python
def read_large_file(path: str):
    with open(path) as f:
        for line in f:
            yield line.strip()
```

### 装饰器
```python
def retry(max_attempts: int = 3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_attempts - 1:
                        raise
            return wrapper
    return decorator
```

---

## 数据处理

### 列表推导
```python
# 简单转换
squares = [x**2 for x in range(10)]

# 带条件
evens = [x for x in range(10) if x % 2 == 0]

# 字典推导
name_lengths = {name: len(name) for name in names}
```

### 数据类
```python
from dataclasses import dataclass

@dataclass
class User:
    id: str
    name: str
    email: str
    active: bool = True
```

---

## 错误处理

```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error")
    raise RuntimeError("Operation failed") from e
finally:
    cleanup()
```

---

## 项目结构

```
project/
├── src/
│   └── package/
│       ├── __init__.py
│       ├── main.py
│       └── utils.py
├── tests/
│   └── test_main.py
├── pyproject.toml
└── README.md
```
