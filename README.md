# <img src="https://raw.githubusercontent.com/HanaokaYuzu/NovelAI-API/master/docs/assets/novelai-logo.svg" height="35px" alt="NovelAI Icon"/> NovelAI-API

A lightweight asynchronous Python wrapper for NovelAI image generation API.

## Features

- **Lightweight** - Focuses on image generation only, providing a simple and easy-to-use interface.
- **Concurrent** - Supports both API and web backend, allowing to run two generating tasks simultaneously.
- **Parameterized** - Provides a `Metadata` class to easily set up generation parameters with type validation.
- **Asynchronous** - Utilizes `asyncio` to run generating tasks and return outputs efficiently.

> [!IMPORTANT]
>
> Unfortunately, NovelAI has depreciated their image generation function of the API endpoint starting from Mar 21, 2024. As a result, concurrent generation feature is no longer available.
>
> [Source](https://twitter.com/novelaiofficial/status/1760404186066227673)

## Table of Contents

- [Features](#features)
- [Table of Contents](#table-of-contents)
- [Installation](#installation)
- [Usage](#usage)
  - [Initialization](#initialization)
  - [Image Generation](#image-generation)
  - [Image to Image](#image-to-image)
  - [Inpainting](#inpainting)
  - [Vibe Transfer](#vibe-transfer)
  - [Use in CLI](#use-in-cli)
- [References](#references)

## Installation

> [!NOTE]
>
> This package requires Python 3.12 or higher.

Install/update with pip:

```sh
pip install -U novelai
```

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
from novelai import Metadata, Resolution

async def main():
    metadata = Metadata(
        prompt="1girl",
        negative_prompt="bad anatomy",
        res_preset=Resolution.NORMAL_PORTRAIT,
        n_samples=1,
    )

    print(f"Estimated Anlas cost: {metadata.calculate_cost(is_opus=False)}")

    output = await client.generate_image(
        metadata, verbose=False, is_opus=False
    )

    for image in output:
        image.save(path="output images", verbose=True)

asyncio.run(main())
```

### Image to Image

To perform `img2img` action, set `action` parameter in Metadata to `Action.IMG2IMG`, and `image` parameter to your base image. The base image  needs to be converted into Base64-encoded format. This can be achieved using `base64` module.

```python
import base64
from novelai import Metadata, Action

async def main():
    with open("tests/images/portrait.jpg", "rb") as f:
        base_image = base64.b64encode(f.read()).decode("utf-8")

    metadata = Metadata(
        prompt="1girl",
        negative_prompt="bad anatomy",
        action=Action.IMG2IMG,
        width=832,
        height=1216,
        n_samples=1,
        image=base_image,
        strength=0.5,
        noise=0.1,
    )

    output = await client.generate_image(metadata, verbose=True)

    for image in output:
        image.save(path="output images", verbose=True)

asyncio.run(main())
```

### Inpainting

To perform `inpaint` action, set `action` parameter in Metadata to `Action.INPAINTING`, and `image` parameter to your base image, and `mask` parameter to the black and white [mask image](https://github.com/HanaokaYuzu/NovelAI-API/blob/master/tests/images/inpaint_left.jpg), where white is the area to inpaint and black to keep as is. Both base image and mask need to be converted into Base64-encoded format. This can be achieved using `base64` module.

```python
import base64
from novelai import Metadata, Model, Action, Resolution

async def main():
    with open("tests/images/portrait.jpg", "rb") as f:
        base_image = base64.b64encode(f.read()).decode("utf-8")

    with open("tests/images/inpaint_left.jpg", "rb") as f:
        mask = base64.b64encode(f.read()).decode("utf-8")

    metadata = Metadata(
        prompt="1girl",
        negative_prompt="bad anatomy",
        model=Model.V3INP,
        action=Action.INPAINT,
        res_preset=Resolution.NORMAL_PORTRAIT,
        image=base_image,
        mask=mask,
    )

    output = await client.generate_image(metadata, verbose=True)

    for image in output:
        image.save(path="output images", verbose=True)

asyncio.run(main())
```

### Vibe Transfer

Vibe transfer doesn't have its own action type. Instead, it is achieved by adding a `reference_image` parameter in Metadata. The reference image needs to be converted into Base64-encoded format. This can be achieved using `base64` module.

```python
import base64
from novelai import Metadata, Resolution

async def main():
    with open("tests/images/portrait.jpg", "rb") as f:
        base_image = base64.b64encode(f.read()).decode("utf-8")

    metadata = Metadata(
        prompt="1girl",
        negative_prompt="bad anatomy",
        res_preset=Resolution.NORMAL_PORTRAIT,
        reference_image=base_image,
        reference_infomation_extracted=1,
        reference_strength=0.6,
    )

    output = await client.generate_image(metadata, verbose=True)

    for image in output:
        image.save(path="output images", verbose=True)

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
