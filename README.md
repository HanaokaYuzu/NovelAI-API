# <img src="https://raw.githubusercontent.com/HanaokaYuzu/NovelAI-API/master/docs/img/novelai-logo.svg" height="35px" alt="NovelAI Icon"/> NovelAI-API

A lightweight asynchronous Python wrapper for NovelAI image generation API.

## Features

- **Lightweight** - Focuses on image generation only, providing a simple and easy-to-use interface.
- **Concurrent** - Supports both API and web backend, allowing to run two generating tasks simultaneously.
- **Parameterized** - Provides a `Metadata` class to easily set up generation parameters with type validation.
- **Asynchronous** - Utilizes `asyncio` to run generating tasks and return outputs efficiently.

## Installation

Install with pip:

```sh
pip install novelai
```

Note that this package requires Python **3.12** or higher. For Python 3.7-3.11, install the legacy version instead:

```sh
pip install novelai-legacy
```

Legacy branch has the same features as master branch on user side, the only difference is code compatibility.

## Usage

### Initialization

Import required packages and initialize a client with your NovelAI account credentials.

```python
import asyncio
from novelai import NAIClient

# Replace argument values with your actual account credentials
username = "Your NovelAI username"
password = "Your NovelAI password"

async def main():
    client = NAIClient(username, password, proxy=None)
    await client.init(timeout=30)

asyncio.run(main())
```

### Image Generation

After initializing successfully, you can generate images with the `generate_image` method. The method takes a `Metadata` object as the first argument, and an optional `host` argument to specify the backend to use.

By passing `verbose=True`, the method will print the estimated Anlas cost each time a generating request is going to be made.

The full parameter list of `Metadata` can be found in the [class definition](https://github.com/HanaokaYuzu/NovelAI-API/blob/master/src/novelai/metadata.py).

```python
from pathlib import Path
from novelai import Metadata, HOSTS

async def main():
    metadata = Metadata(
        prompt="1girl",
        negative_prompt="bad anatomy",
        width=832,
        height=1216,
        n_samples=1,
    )

    print(f"Estimated Anlas cost: {metadata.calculate_cost(is_opus=False)}")

    # Choose host between "HOSTS.API" and "HOSTS.WEB"
    output = await client.generate_image(
        metadata, host=HOSTS.WEB, verbose=False, is_opus=False
    )

    path = Path("./temp")
    path.mkdir(parents=True, exist_ok=True)

    for filename, data in output.items():
        dest = Path(path / filename)
        dest.write_bytes(data)
        print(f"Image saved as {dest.resolve()}")

asyncio.run(main())
```

### Concurrent Generation

By default, NovelAI only allows one concurrent generating task at a time. However, this wrapper provides the ability to **simultaneously run two concurrent generating tasks** by sending requests to API and web backend respectively.

Note that API and web backend both have limit on concurrent generation. Therefore, running more than two concurrent tasks will result in a `429 Too Many Requests` error.

[Full usage example](https://github.com/HanaokaYuzu/NovelAI-API/blob/master/docs/concurrent_generation.py) is provided under `/docs`.

```python
async def task_api():
    await client.generate_image(metadata, host=HOSTS.API)
    print("API task completed")

async def task_web():
    await client.generate_image(metadata, host=HOSTS.WEB)
    print("Web task completed")

async def main():
    tasks = [
        asyncio.create_task(task_api()),
        asyncio.create_task(task_web()),
    ]
    await asyncio.wait(tasks)

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
