# cerul-python

Official Python SDK for the Cerul video search API.

## Requirements

- Python 3.9+
- A Cerul API key

## Install

```bash
pip install cerul
```

## Quick Start

```python
from cerul import Cerul

client = Cerul(api_key="cerul_sk_...")

result = client.search(
    query="Sam Altman on AI video tools",
    max_results=5,
    include_answer=True,
    filters={"speaker": "Sam Altman"},
)

print(result.results[0].title if result.results else "No results")

usage = client.usage()
print(f"{usage.credits_used}/{usage.credits_limit}")
```

If `api_key` is omitted, the SDK reads `CERUL_API_KEY` from the environment.

## Async Usage

```python
import asyncio

from cerul import AsyncCerul


async def main() -> None:
    async with AsyncCerul(api_key="cerul_sk_...") as client:
        result = await client.search(query="computer vision", max_results=3)
        print(len(result.results))


asyncio.run(main())
```

## Configuration

```python
from cerul import Cerul

client = Cerul(
    api_key="cerul_sk_...",
    base_url="https://api.cerul.ai",
    timeout=30.0,
    retry=False,
)
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m unittest discover -s tests
python -m build
```
