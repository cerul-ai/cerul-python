<div align="center">
  <br />
  <a href="https://cerul.ai">
    <img src="https://raw.githubusercontent.com/cerul-ai/cerul/main/assets/logo.png" alt="Cerul" width="80" />
  </a>
  <h1>Cerul Python SDK</h1>
  <p><strong>The video search layer for AI agents.</strong></p>

  <p>
    <a href="https://pypi.org/project/cerul/"><img alt="PyPI" src="https://img.shields.io/pypi/v/cerul?style=flat-square&color=3b82f6" /></a>
    <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-3b82f6?style=flat-square" /></a>
    <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-22c55e?style=flat-square" />
  </p>

  <p>
    <a href="https://cerul.ai/docs">Docs</a> &middot;
    <a href="https://cerul.ai">Website</a> &middot;
    <a href="https://github.com/cerul-ai/cerul">GitHub</a>
  </p>
</div>

<br />

Search what was said, shown, or presented in any video — tech talks, podcasts, conference presentations, and earnings calls.

```bash
pip install cerul
```

```python
from cerul import Cerul

client = Cerul()  # reads CERUL_API_KEY

for r in client.search(query="Sam Altman on AGI timeline"):
    print(r.title, r.url)
```

Get a free API key at [cerul.ai/dashboard](https://cerul.ai/dashboard).

## Examples

```python
# Search with filters
result = client.search(
    query="Jensen Huang on AI infrastructure",
    max_results=5,
    ranking_mode="rerank",
    include_answer=True,
    filters={"speaker": "Jensen Huang", "published_after": "2024-01-01"},
)

# AI-generated answer
print(result.answer)

# Results print as JSON
print(result[0])

# Check credits
usage = client.usage()
print(f"{usage.credits_remaining} credits remaining")
```

## Async

```python
from cerul import AsyncCerul

async with AsyncCerul() as client:
    result = await client.search(query="attention mechanism explained")
```

## Configuration

```python
client = Cerul(
    api_key="cerul_sk_...",   # or CERUL_API_KEY env var
    timeout=30.0,             # default 30s
    retry=True,               # retry 429/5xx/network errors
)
```

## Error handling

```python
from cerul import CerulError

try:
    client.search(query="test")
except CerulError as e:
    print(e.status_code, e.code, e.message)
```

## Links

- [TypeScript SDK](https://www.npmjs.com/package/cerul) — `npm install cerul`
- [CLI](https://github.com/cerul-ai/cerul-cli) — `curl -fsSL .../install.sh | bash`
- [Main repo](https://github.com/cerul-ai/cerul) — API, docs, skills, remote MCP

## License

[MIT](./LICENSE)
