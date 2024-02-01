import os
import asyncio
from pathlib import Path

from loguru import logger

from novelai import NAIClient, Metadata, HOSTS


@logger.catch
async def main():
    client = NAIClient(
        username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"), timeout=30
    )
    await client.init()

    metadata = Metadata(
        prompt=os.getenv("PROMPT"),
        negative_prompt=os.getenv("NEGATIVE_PROMPT"),
        qualityToggle=False,
        ucPreset=3,
        width=832,
        height=1216,
        n_samples=1,
        sm_dyn=True,
    )
    output = await client.generate_image(
        metadata, host=HOSTS.WEB, verbose=True, is_opus=True
    )

    path = Path("./temp")
    path.mkdir(parents=True, exist_ok=True)

    for filename, data in output.items():
        Path(path / filename).write_bytes(data)
        logger.success(f"Image saved as {path / filename}")


if __name__ == "__main__":
    asyncio.run(main())
