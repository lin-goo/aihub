# AIHub - AI服务通信封装

AIHub 是一个Python库，它提供了与AI服务提供商进行交互的端点（Endpoint）和对话（Dialogue）管理器。这个库旨在简化与OpenAI和百度等服务提供商的通信过程，封装发送消息和接收回复的复杂细节。

## 功能

- **Endpoint** 类：用于封装与特定AI服务提供商的通信。
  - 支持多种服务提供商，包括OpenAI和百度。
  - 异步发送消息并获取响应。
  - 从JSON配置文件中加载和保存端点配置。配置文件可参考[example.json](example.json)。

- **Dialogue** 类：用于管理与AI服务的对话，自动处理消息上下文。
  - 发送消息，并通过异步或回调的方式接收回复。
  - 维护消息和回复的历史列表。

## 使用样例
### 创建并使用Endpoint
```python
import asyncio
from AIHub import Endpoint

async def main():
  # 从JSON配置文件加载
  endpoint = Endpoint.load_from_json('config.json')
  
  # 使用配置创建Endpoint
  my_endpoint = Endpoint(name="openai.official", provider="openai", api_key="sk-xxx", model="gpt-4-1106-preview")
  
  # 通过Endpoint实例发送消息列表，接收纯文本的应答
  response = await endpoint.send_message([{"role": "user", "content": "你好！"}], only_text=True)
  print("Received response:", response)

if __name__ == '__main__':
  asyncio.run(main())
```

### 创建并使用Dialogue
```python
import asyncio
from AIHub import Dialogue, Endpoint

async def dialogue_example():
    # 通过已有的endpoint实例，创建Dialogue实例
    my_endpoint = Endpoint(name="openai.official", provider="openai", api_key="sk-xxx", model="gpt-4-1106-preview")
    dialogue = Dialogue(endpoint=my_endpoint)
    
    # 或者直接读取本地Endpoint配置文件，创建Dialogue实例
    dialogue = Dialogue(endpoint_config_path='config.json')

    # 异步发送消息并获取纯文本回复
    response = await dialogue.send_message_async("你好！你是谁？")
    print("Received response:", response)

    # 使用回调函数发送消息
    def my_callback(res):
        print("Received response with callback:", res)

    dialogue.send_message_with_callback("你好！你是谁？", my_callback)

asyncio.run(dialogue_example())
```

### 获取所有对话历史
```python
from AIHub import Dialogue

dialogue = Dialogue(endpoint_config_path='config.json')
# 若干次对话后……
messages_history = dialogue.get_messages()
print("Dialogue history:", messages_history)
```

## 文档
### Dialogue 类

Dialogue 类是用于与AI服务提供商进行交互的会话管理器。它封装了发送消息和接收回复的过程，并维护了一个消息历史列表。通过这个类，用户可以发送消息，以异步或回调的方式接收回复，并且该类将自动管理历史消息上下文。

构造函数参数:

- endpoint (Endpoint, 可选): 已经实例化的Endpoint对象，用于发送和接收消息。
- endpoint_config_path (str, 可选): 一个JSON格式的配置文件路径，包含创建Endpoint所需的配置信息。

实例属性:

- messages (List[Dict[str, str]]): 存储对话中的消息和回复的历史列表。

实例方法:

- get_messages() -> List[Dict[str, str]]:
    - 返回对话中的消息和回复的历史列表。

- async send_message_async(message: str) -> str:
    - 异步发送消息到与Dialogue关联的Endpoint，并等待回复。
    - message 参数是要发送的文本消息。
    - 此方法会将发送的消息和接收的回复添加到Dialogue实例的消息历史中。
    - 返回从Endpoint接收到的回复。

- send_message_with_callback(message: str, callback: Callable[[str], None]) -> None:
    - 发送消息，并在接收到回复时调用指定的回调函数。
    - message 参数是要发送的文本消息。
    - callback 参数是一个回调函数，它接受一个字符串参数，即从Endpoint接收到的回复。


### Endpoint 类
Endpoint 类是一个对AI服务通信的高级封装，它可以直接与不同的AI服务提供商的不同模型进行交流，并提供了简洁的接口。目前支持的服务提供商有OpenAI和百度（Baidu）。

类方法:

- load_from_json(file_path: str) -> 'Endpoint':
    - 从一个JSON格式的配置文件中加载端点的配置信息，创建并返回一个Endpoint实例。
    - file_path 参数是配置文件的路径。

- save_to_json(endpoint: 'Endpoint', file_path: str) -> None:
    - 将Endpoint实例的配置信息保存到一个JSON格式的配置文件中。
    - endpoint 参数是一个Endpoint实例，file_path 参数是配置文件的路径。

- load_list_from_json(file_path: str) -> List['Endpoint']:
    - 从一个JSON格式的配置文件中加载多个端点的配置信息，创建并返回一个包含多个Endpoint实例的列表。
    - file_path 参数是配置文件的路径。

- save_list_to_json(endpoints: List['Endpoint'], file_path: str) -> None:
    - 将多个Endpoint实例的配置信息保存到一个JSON格式的配置文件中。
    - endpoints 参数是一个包含多个Endpoint实例的列表，file_path 参数是配置文件的路径。

实例方法:

- async send_message(message: Any, **kwargs) -> Any:
    - 异步发送消息到配置的服务提供商，并返回响应。
    - message 参数是要发送的消息，其格式多数情况下为一个字典列表，例如[{"role":"user","content":"Hello!"}]。注意：该接口不提供上下文管理，在调用时需要将整个对话的消息列表作为参数传入。
    - kwargs 参数用于提供额外的选项，这些选项可以包括:
        - only_text (bool): 如果设置为True（默认值），则只返回纯文本响应。如果设置为False，则返回服务提供商原始的响应数据结构。

构造函数参数:

- name (str): 端点的名称。由用户自行定义与识别，与服务商的模型名称无关。
- provider (str): 服务提供商的名称，目前支持'openai'和'baidu'。
- api_key (str): 服务提供商的API密钥。
- model (str): 指定服务使用的模型。
- org_id (str, 可选): 组织ID，仅在使用OpenAI服务时需要。
- api_base (str, 可选): API的基础URL，如果使用除默认之外的URL时提供。仅在使用OpenAI服务时需要。
- secret_key (str, 可选): 服务提供商的密钥，仅在使用百度服务时需要。
