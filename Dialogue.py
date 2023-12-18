import asyncio
from typing import Callable
from loguru import logger

from .Endpoint import Endpoint


class Dialogue:
    def __init__(self, endpoint: Endpoint = None, endpoint_config_path: str = None):
        self.messages = []
        if not endpoint_config_path and not endpoint:
            raise ValueError("Either endpoint or endpoint_path must be specified")
        if endpoint_config_path and not endpoint:
            endpoint = Endpoint.load_from_json(endpoint_config_path)
        self.endpoint = endpoint

    def get_messages(self):
        return self.messages

    async def send_message_async(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        logger.debug(f"Sending message {message} to endpoint {self.endpoint.name}")
        response = await self.endpoint.send_message(self.messages, only_text=True)
        logger.debug(f"Received response {response} from endpoint {self.endpoint.name}")
        self.messages.append({"role": "assistant", "content": response})
        return response

    def send_message_with_callback(self, message: str, callback: Callable[[str], None]) -> None:
        def complete_callback(f):
            response = f.result()
            callback(response)

        future = asyncio.ensure_future(self.send_message_async(message))
        future.add_done_callback(complete_callback)
