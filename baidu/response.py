from dataclasses import dataclass


@dataclass()
class LLMResponse:
    content: str = None
    tokens: int = None
    error: str = None

