import os
import asyncio

from loguru import logger

from novelai import NAIClient, Metadata, Host


client = NAIClient(
    username=os.getenv("USERNAME"), password=os.getenv("PASSWORD")
)


@logger.catch
async def task_api():
    metadata = Metadata(
        prompt=os.getenv("PROMPT"),
        negative_prompt=os.getenv("NEGATIVE_PROMPT"),
    )

    output = await client.generate_image(
        metadata, host=Host.API, verbose=True, is_opus=True
    )

    for image in output:
        image.save(verbose=True)

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
        metadata, host=Host.WEB, verbose=True, is_opus=True
    )

    for image in output:
        image.save(verbose=True)

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
