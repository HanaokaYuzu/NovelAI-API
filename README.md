# <a style="background-color: rgb(25, 27, 49); border-radius: 5px;padding-left: 5px; padding-right: 5px; padding-top: 8px;"><img src="https://novelai.net/_next/static/media/pen-tip-light.47883c90.svg" height="30px" alt="NovelAI Icon"/></a> NovelAI-API

A lightweight asynchronous Python wrapper for the NovelAI image generation API supporting both web and api backend.

## Installation

```bash
pip install novelai
```

## Usage

### Initialization

```python
import asyncio
from novelai import NAIClient

# Replace string values with your actual account credentials
username = "Your NovelAI username"
password = "Your NovelAI password"

async def main():
    client = NAIClient(username, password, proxy=None)
    await client.init()

asyncio.run(main())
```

### Generate

```python
from pathlib import Path

async def main():
    output = await client.generate_image(prompt="1girl", host="api")  # Choose host between "api" and "web"

    path = Path("output")
    path.mkdir(parents=True, exist_ok=True)

    for filename, data in output.items():
        Path(path / filename).write_bytes(data)

asyncio.run(main())
```

## References

[NovelAI Backend](https://api.novelai.net/docs)

[Aedial/novelai-api](https://github.com/Aedial/novelai-api)

[NovelAI Unofficial Knowledgebase](https://naidb.miraheze.org/wiki/Using_the_API)
