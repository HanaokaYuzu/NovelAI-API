# <img src="https://raw.githubusercontent.com/HanaokaYuzu/NovelAI-API/master/docs/img/novelai-logo.svg" height="35px" alt="NovelAI Icon"/> NovelAI-API

A lightweight asynchronous Python wrapper for NovelAI image generation API. Supports both web and api backend.

## Installation

```sh
pip install novelai
```

## Usage

### Initialization

```python
import asyncio
from novelai import NAIClient

# Replace argument values with your actual account credentials
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
    # Choose host between "api" and "web"
    output = await client.generate_image(prompt="1girl", host="api")

    path = Path("output")
    path.mkdir(parents=True, exist_ok=True)

    for filename, data in output.items():
        Path(path / filename).write_bytes(data)

asyncio.run(main())
```

### Use in CLI

Optionally, a module function is also provided to directly generate access token in CLI.

Once a access token is generated, it will be valid for 30 days. Token can be used as the authentication header to make requests to NovelAI.

```sh
# Replace argument values with your actual account credentials
python3 -m novelai login <username> <password>
```

## References

[NovelAI Backend](https://api.novelai.net/docs)

[Aedial/novelai-api](https://github.com/Aedial/novelai-api)

[NovelAI Unofficial Knowledgebase](https://naidb.miraheze.org/wiki/Using_the_API)
