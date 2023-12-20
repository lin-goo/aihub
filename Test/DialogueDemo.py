import asyncio
from AIHub import Dialogue, Endpoint


async def dialogue_example():
    # 直接读取本地Endpoint配置文件，创建Dialogue实例
    dialogue = Dialogue(endpoint_config_path='../LocalConfig/baidu.json')

    # 异步发送消息并获取纯文本回复
    response = await dialogue.send_message_async("你好！你是谁？")
    print("Received response:", response)

    # 再次发送消息，并使用回调函数处理回复
    # Dialogue会自动维护消息历史，因此AI服务可以根据上下文进行回复
    def my_callback(res):
        print("Received response with callback:", res)

    dialogue.send_message_with_callback("刚刚我说了啥？", my_callback)

    await asyncio.sleep(10)


asyncio.run(dialogue_example())
