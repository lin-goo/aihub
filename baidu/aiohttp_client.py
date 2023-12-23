from typing import Union

from aiohttp import ClientSession, TCPConnector

cs: Union[ClientSession, None] = None


async def get_session() -> ClientSession:
    global cs
    if cs is None:
        cs = ClientSession(connector=TCPConnector(verify_ssl=False))
    return cs
