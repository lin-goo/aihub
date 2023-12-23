import asyncio
import datetime
import json
import time
from asyncio import Queue, Task, Future

from loguru import logger
from typing import List, Dict, Union, Tuple
from baidu.aiohttp_client import get_session
from config import settings
from .response import LLMResponse


class BaiduMessageSender:

    support_type: set = set(settings.baidu_prompts)

    @classmethod
    async def create(cls, name: str, api_key: str, secret_key: str, queue: Queue, max_calls_per_second: int = 2):
        self = cls(api_key=api_key, secret_key=secret_key, name=name,
                   queue=queue, max_calls_per_second=max_calls_per_second)
        await self.check_and_refresh_token()
        self.background_task = asyncio.create_task(self.start_consume())
        return self

    async def close(self):
        self.background_task.cancel()

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name}"

    def __init__(self, name: str, api_key: str, secret_key: str,
                 queue: Queue, max_calls_per_second: int, **kwargs):
        """

        :param name: 实例名称
        :param api_key:
        :param secret_key:
        :param queue: 所有百度实例共享的队列
        :param prompts_config_path: 提示词加载
        :param max_calls_per_second:
        :param kwargs:
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self.token_obtained_time = None
        self.name: str = name
        self.background_task: Union[Task, None] = None
        self.queue: Queue[Tuple[Future, List[Dict[str, str]]]] = queue
        self.timestamps = []
        self.max_calls_per_second: int = max_calls_per_second

    @staticmethod
    async def _get_access_token(api_key: str, secret_key: str):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
        session = await get_session()
        async with session.post(url, params=params) as response:
            response_json = await response.json()
            return response_json.get("access_token"), datetime.datetime.now()

    async def check_and_refresh_token(self):
        if self.access_token is None or (datetime.datetime.now() - self.token_obtained_time).days >= 25:
            self.access_token, self.token_obtained_time = await self._get_access_token(self.api_key, self.secret_key)
            logger.debug("Refreshing Baidu access token")

    async def _send_message(self, future: Future, message: List[Dict[str, str]], **kwargs) -> None:
        await self.check_and_refresh_token()
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/" \
              f"wenxinworkshop/chat/completions_pro?access_token={self.access_token}"
        payload = json.dumps({"messages": message})
        headers = {'Content-Type': 'application/json'}
        session = await get_session()
        async with session.post(url, headers=headers, data=payload) as response:
            response_json = await response.json()
            logger.info(response_json)
            if future.cancelled():
                logger.warning(f"BaiduEndpoint: future cancelled: {message[:10]}")
                return

            if "result" not in response_json:
                logger.error(response_json)
                future.set_result(LLMResponse(error=str(response_json)))  # content = None
            else:
                future.set_result(LLMResponse(content=response_json["result"],
                                              tokens=response_json['usage']['total_tokens']))

    async def _send_from_queue(self):
        logger.info(f"{self.name}: 开始等待新任务")
        future, message = await self.queue.get()
        if future.cancelled():
            logger.warning(f"{self.name}: 忽略超时任务")
            return False
        asyncio.create_task(self._send_message(future=future, message=message))
        return True

    async def start_consume(self):
        logger.info(f"启动：{self.name} 循环")
        while True:
            can_consume, now = self.can_consume_task()
            if can_consume:
                if await self._send_from_queue():  # 拿到的future没有cancel
                    self.timestamps.append(now)
                else:  # future已经cancel
                    continue  # 无需等待，继续刷新timestamps并尝试重新获取数据
            else:
                await asyncio.sleep(0.3)

    def can_consume_task(self) -> Tuple[bool, float]:
        """更新状态，如果有能力消费数据就返回True， 负载上限就返回False"""
        # 丢掉一秒之前的数据
        now = time.time()
        self.timestamps[:] = [t for t in self.timestamps if now - t < 1]
        if len(self.timestamps) < self.max_calls_per_second:
            return True, now
        else:
            return False, now

    @staticmethod
    def _replace_placeholders(template: str, values: Dict[str, str]) -> str:
        # 将模板字符串中的占位符替换为values字典中的值
        result = template
        if not values:
            return result
        for key, value in values.items():
            result = result.replace(f'{{{key}}}', value)
        return result
