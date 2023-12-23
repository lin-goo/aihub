import asyncio
from asyncio import Future, Queue
from typing import List, Union, Tuple, Dict

import yaml
from loguru import logger
from .baidu_endpoint import BaiduMessageSender
from config import settings
from .response import LLMResponse


class BaiduManager:
    """百度实例管理程序"""

    support_type: set = set(settings.baidu_prompts)

    @classmethod
    async def create(cls, prompts_config_path: str, ):
        self = cls(prompts_config_path=prompts_config_path)
        await self._load_instances()
        return self

    async def close(self):
        for instance in self._baidu_instance:
            await instance.close()

    def __init__(self, prompts_config_path: str):
        self._baidu_instance: List[BaiduMessageSender] = []
        with open(prompts_config_path, 'r', encoding='utf-8') as file:
            self._prompts = yaml.safe_load(file)
        self._queue: Queue[Tuple[Future, List[Dict[str, str]]]] = Queue()

    async def _load_instances(self):
        """加载百度实例"""
        for cfg in settings.baidu:
            if cfg.name != "未知用户":
                bms = await BaiduMessageSender.create(name=cfg.name, queue=self._queue,
                                                      api_key=cfg.api_key, secret_key=cfg.secret_key)
                self._baidu_instance.append(bms)

    async def request(self, message: str, prompts_type: str) -> LLMResponse:
        """提示词替换和发送"""
        if prompts_type in self.support_type:
            prepared_message = self._replace_one_arg_message(
                prompts=getattr(settings.baidu_prompts, prompts_type),
                message=message
            )
            return await self._request(message=[{"role": "user", "content": prepared_message}])
        else:
            error = f"BaiduManager: unsupported type: {prompts_type}"
            logger.error(error)
            return LLMResponse(error=error)

    async def _request(self, message: List[Dict[str, str]]) -> LLMResponse:
        """
        请求文心一言获取数据的
        :param message: 用户输入
        :return: 成功时返回 (llm返回的文本， 消耗的总tokens数)， 失败时返回 None
        """
        future = asyncio.get_event_loop().create_future()
        logger.info(f"BaiduManager: request: {message[:10]}")
        await self._queue.put((future, message))
        try:
            return await asyncio.wait_for(future, 10)  # 等待这个任务5秒，超时会触发TimeoutError
        except TimeoutError:
            logger.warning(f"request 超时: {message[:10]}")
            return LLMResponse(error="TimeoutError")

    @staticmethod
    def _replace_one_arg_message(prompts: str, message: str) -> str:
        return prompts.replace("{content}", message)


baidu_manager: Union[None, BaiduManager] = None


async def get_baidu_manager(prompts_config_path: str):
    global baidu_manager
    if baidu_manager is None:
        baidu_manager = await BaiduManager.create(prompts_config_path=prompts_config_path)
    return baidu_manager
