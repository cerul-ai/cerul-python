<div align="center">
  <h1>cerul</h1>
  <p><strong>The video search layer for AI agents — Python SDK.</strong></p>
  <p>Teach your AI agents to see. Search what was said, shown, or presented in any video.</p>

  <p>
    <a href="https://cerul.ai/docs"><strong>Docs</strong></a> &middot;
    <a href="https://cerul.ai"><strong>Website</strong></a> &middot;
    <a href="https://github.com/cerul-ai/cerul"><strong>Main Repo</strong></a> &middot;
    <a href="https://github.com/cerul-ai/cerul-cli"><strong>CLI</strong></a>
  </p>

  <p>
    <a href="https://pypi.org/project/cerul/"><img alt="PyPI" src="https://img.shields.io/pypi/v/cerul?style=flat-square&color=3b82f6" /></a>
    <a href="https://pypi.org/project/cerul/"><img alt="Downloads" src="https://img.shields.io/pypi/dm/cerul?style=flat-square&color=22c55e" /></a>
    <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-3b82f6?style=flat-square" /></a>
    <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-22c55e?style=flat-square" />
  </p>
</div>

<br />

## What is Cerul?

Cerul indexes tech talks, podcasts, conference presentations, and earnings calls. This SDK lets you search across all of them by meaning — speech, visuals, slides, and on-screen text.

```python
from cerul import Cerul

client = Cerul()
result = client.search(query="Sam Altman on AGI timeline")

for r in result:
    print(f"{r.title} — {r.url}")
```

> **Get your free API key at [cerul.ai/dashboard](https://cerul.ai/dashboard)** — 1,000 credits/month, no credit card.

## Install

```bash
pip install cerul
```

## Quick Start

```python
from cerul import Cerul

client = Cerul()  # reads CERUL_API_KEY from env

# Search videos
result = client.search(
    query="how does attention mechanism work",
    max_results=5,
    include_answer=True,
)

# Iterate directly over results
for r in result:
    print(f"[{r.score:.0%}] {r.title}")
    print(f"  {r.snippet}")
    print(f"  {r.url}")
    print()

# AI-generated answer (when include_answer=True)
if result.answer:
    print(f"Answer: {result.answer}")

# Access results by index
top = result[0]
print(f"Top result: {top.title} ({top.speaker})")

# Result count
print(f"Found {len(result)} results")
```

## Search with Filters

```python
result = client.search(
    query="Jensen Huang on AI infrastructure",
    max_results=10,
    ranking_mode="rerank",          # LLM-based reranking for higher precision
    include_answer=True,            # costs 2 credits instead of 1
    filters={
        "speaker": "Jensen Huang",
        "published_after": "2024-01-01",
        "source": "youtube",
    },
)
```

## Response Format

All responses print as clean JSON:

```python
print(result[0])
```
```json
{
  "id": "unit_hmtuvNfytjM_1223",
  "score": 0.93,
  "url": "https://cerul.ai/v/a8f3k2x",
  "title": "Sam Altman on AGI Timeline",
  "snippet": "AGI is coming sooner than most people expect...",
  "transcript": "AGI is coming sooner than most people expect. I think we're within a few years...",
  "duration": 7200,
  "source": "youtube",
  "speaker": "Sam Altman",
  "timestamp_start": 1223.0,
  "timestamp_end": 1345.0
}
```

Convert to dict or JSON string:

```python
data = result.to_dict()       # plain dict
json_str = result.to_json()   # JSON string
```

## Async

```python
from cerul import AsyncCerul

async with AsyncCerul() as client:
    result = await client.search(query="attention mechanism explained")
    for r in result:
        print(r.title)
```

## Configuration

```python
client = Cerul(
    api_key="cerul_sk_...",     # or reads CERUL_API_KEY env var
    timeout=30.0,               # seconds, default 30
    retry=True,                 # retry on 429/5xx/network errors, default False
)
```

## Usage Monitoring

```python
usage = client.usage()
print(f"Credits: {usage.credits_used} used / {usage.credits_remaining} remaining")
print(f"Daily free: {usage.daily_free_remaining} / {usage.daily_free_limit}")
```

## Error Handling

```python
from cerul import Cerul, CerulError

try:
    client = Cerul()
    result = client.search(query="test")
except CerulError as e:
    print(e.status_code)   # HTTP status (0 for network/timeout)
    print(e.code)          # "unauthorized", "rate_limited", "api_error", etc.
    print(e.message)       # human-readable message
    print(e.request_id)    # for debugging with Cerul support
```

## Features

| Feature | Details |
|---------|---------|
| **Sync + Async** | `Cerul` for synchronous, `AsyncCerul` for async/await |
| **Typed responses** | Dataclass results with full type hints, no pydantic needed |
| **JSON output** | `print(result)` gives formatted JSON, `result.to_dict()` for dicts |
| **Iterable results** | `for r in result`, `result[0]`, `len(result)` |
| **Retry with backoff** | 429 reads `Retry-After` (capped at 60s), 5xx exponential backoff |
| **Network error retry** | Timeouts and connection errors also retried when `retry=True` |
| **Minimal deps** | Only `httpx` — no heavy frameworks |

## Ecosystem

| Package | Install | Description |
|---------|---------|-------------|
| **cerul** (Python) | `pip install cerul` | This package |
| [cerul](https://www.npmjs.com/package/cerul) (TypeScript) | `npm install cerul` | TypeScript SDK |
| [cerul-cli](https://github.com/cerul-ai/cerul-cli) | `curl -fsSL .../install.sh \| bash` | CLI tool (Rust) |
| [cerul](https://github.com/cerul-ai/cerul) | — | Main repo — API, docs, skills, remote MCP |

## License

[MIT](./LICENSE)
