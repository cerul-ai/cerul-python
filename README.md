<div align="center">
  <h1>cerul</h1>
  <p><strong>The video search layer for AI agents — Python SDK.</strong></p>
  <p>Teach your AI agents to see. Search what was said, shown, or presented in any video.</p>

  <p>
    <a href="https://cerul.ai/docs"><strong>Docs</strong></a> &middot;
    <a href="https://cerul.ai"><strong>Website</strong></a> &middot;
    <a href="https://github.com/cerul-ai/cerul"><strong>Main Repo</strong></a>
  </p>

  <p>
    <a href="https://pypi.org/project/cerul/"><img alt="PyPI" src="https://img.shields.io/pypi/v/cerul?style=flat-square&color=3b82f6" /></a>
    <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-3b82f6?style=flat-square" /></a>
    <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-22c55e?style=flat-square" />
  </p>
</div>

<br />

## Install

```bash
pip install cerul
```

## Quick Start

```python
from cerul import Cerul

client = Cerul()  # reads CERUL_API_KEY from env

result = client.search(
    query="Sam Altman on AGI timeline",
    max_results=5,
    include_answer=True,
    filters={"speaker": "Sam Altman"},
)

for r in result.results:
    print(f"{r.title} ({r.score}) — {r.url}")
```

## Features

- **Sync + Async** — `Cerul` for sync, `AsyncCerul` for async
- **Minimal dependencies** — `httpx` only
- **Dataclass responses** — typed results, no pydantic required
- **Timeout** — configurable, default 30s
- **Optional retry** — 429 reads `Retry-After`, 5xx exponential backoff
- **API key resolution** — parameter > `CERUL_API_KEY` env var

## Async

```python
from cerul import AsyncCerul

async with AsyncCerul() as client:
    result = await client.search(query="attention mechanism explained")
    print(len(result.results))
```

## Configuration

```python
client = Cerul(
    api_key="cerul_sk_...",     # or reads CERUL_API_KEY
    timeout=30.0,               # seconds, default 30
    retry=True,                 # retry 429/5xx, default False
)
```

## Usage Monitoring

```python
usage = client.usage()
print(f"{usage.credits_used} / {usage.credits_remaining} credits")
```

## Errors

```python
from cerul import Cerul, CerulError

try:
    Cerul().search(query="test")
except CerulError as e:
    print(e.status_code, e.code, e.message)
```

## Ecosystem

| Package | Description |
|---------|-------------|
| [`cerul`](https://github.com/cerul-ai/cerul) | Main repo — API, docs, skills, remote MCP |
| [`cerul`](https://www.npmjs.com/package/cerul) | TypeScript SDK |
| [`cerul-cli`](https://github.com/cerul-ai/cerul-cli) | CLI tool (Rust) |

## License

[MIT](./LICENSE)
