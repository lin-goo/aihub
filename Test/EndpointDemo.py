import asyncio
from AIHub import Endpoint


async def endpoint_example():
    baidu_endpoint = Endpoint.load_from_yaml('../LocalConfig/baidu_endpoint.yaml')
    response = await baidu_endpoint.send_message([{"role": "user", "content": "你好！你是谁？"}], only_text=True)
    print("Received response:", response)

    openai_endpoint = Endpoint.load_from_yaml('../LocalConfig/openai_official.yaml')
    response = await openai_endpoint.send_message([{"role": "user", "content": "你好！你是谁？"}], only_text=True)
    print("Received response:", response)

    openai_endpoint = Endpoint.load_from_yaml('../LocalConfig/openai_mirror_1.yaml')
    response = await openai_endpoint.send_message([{"role": "user", "content": "你好！你是谁？"}], only_text=True)
    print("Received response:", response)


if __name__ == '__main__':
    asyncio.run(endpoint_example())
