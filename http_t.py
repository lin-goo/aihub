import asyncio
from baidu import get_baidu_manager
from loguru import logger
from asyncio import Queue


async def do2(bm):
    r = await bm.request(message="自信心培养", prompts_type="proofreading")
    logger.info(r)


async def do():
    bm = await get_baidu_manager(prompts_config_path="baidu/chat_prompts.yaml")
    bm.request()
    for i in range(20):
        asyncio.create_task(do2(bm))

    await asyncio.sleep(1000)


async def main():
    queue = Queue()
    future_list = []
    for i in range(10):
        future = asyncio.get_event_loop().create_future()
        future_list.append(future)
        await queue.put(future)

    print(queue.qsize())

    for i in range(5):
        future_list[i].cancel()

    print(queue.qsize())


asyncio.run(do())
