import asyncio
from AIHub import Endpoint


async def endpoint_example():
    endpoint = Endpoint.load_from_json('../LocalConfig/baidu.json')

    response = await endpoint.send_message([{"role": "user", "content": "你好！"}], only_text=True)
    print("Received response:", response)

asyncio.run(endpoint_example())
