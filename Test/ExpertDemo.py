import asyncio
from AIHub import Expert


async def expert_example():
    # 创建 Expert 实例，加载 prompts
    expert = Expert(endpoint_config_path="../LocalConfig/baidu_endpoint.yaml",
                    prompts_config_path="../LocalConfig/chat_prompts.yaml")

    # 使用communicate方法，发送指定Prompt的消息，接收纯文本的应答
    # expert将自动维护上下文
    get_notice_response = await expert.communicate(prompt_type="notice", prompt_params={"content": "明天放假"})
    print(get_notice_response)

    get_len_response = await expert.communicate(message="刚刚生成的通知有多少字？")
    print(get_len_response)

    # 使用get_answer方法，发送指定Prompt的消息，接收纯文本的应答
    # 该函数为一次性调用，不会维护上下文
    get_extend_response = await expert.get_answer(prompt_type="extend", prompt_params={"content": "思维导图是一种清晰的思维表达方式"})
    print(get_extend_response)

    get_len_response = await expert.get_answer(message="刚刚扩写的内容有多少字？")  # 该函数无上下文，因此无法获得扩写内容字数
    print(get_len_response)


# 运行主程序
asyncio.run(expert_example())
