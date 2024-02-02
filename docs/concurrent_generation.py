import os
import asyncio
from pathlib import Path

from loguru import logger

from novelai import NAIClient, Metadata, HOSTS


client = NAIClient(
    username=os.getenv("USERNAME"), password=os.getenv("PASSWORD")
)

path = Path("./temp")
path.mkdir(parents=True, exist_ok=True)


@logger.catch
async def task_api():
    metadata = Metadata(
        prompt=os.getenv("PROMPT"),
        negative_prompt=os.getenv("NEGATIVE_PROMPT"),
    )

    output = await client.generate_image(
        metadata, host=HOSTS.API, verbose=True, is_opus=True
    )

    for filename, data in output.items():
        dest = Path(path / f"api_{filename}")
        dest.write_bytes(data)
        logger.info(f"Image saved as {dest.resolve()}")

    logger.success("API task completed!")


@logger.catch
async def task_web():
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

    for filename, data in output.items():
        dest = Path(path / f"web_{filename}")
        dest.write_bytes(data)
        logger.info(f"Image saved as {dest.resolve()}")

    logger.success("Web task completed!")


@logger.catch
async def main():
    await client.init(timeout=45)
    tasks = [
        asyncio.create_task(task_api()),
        asyncio.create_task(task_web()),
    ]
    await asyncio.wait(tasks)


if __name__ == "__main__":
    asyncio.run(main())
