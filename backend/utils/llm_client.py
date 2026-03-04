"""
Unified LLM Client for multiple providers
Supports: ZhipuAI, Kimi, DeepSeek, Doubao
"""
import json
from typing import List, Dict, Generator, Optional
from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Base class for LLM clients"""

    def __init__(self, api_key: str, model: str, base_url: str = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    @abstractmethod
    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """Send chat request and return response"""
        pass

    @abstractmethod
    def chat_stream(self, messages: List[Dict], temperature: float = 0.7) -> Generator[str, None, None]:
        """Send chat request and return streaming response"""
        pass


class OpenAICompatibleClient(BaseLLMClient):
    """Client for OpenAI-compatible APIs (Kimi, DeepSeek, Doubao)"""

    def __init__(self, api_key: str, model: str, base_url: str):
        super().__init__(api_key, model, base_url)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")

    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")

    def chat_stream(self, messages: List[Dict], temperature: float = 0.7) -> Generator[str, None, None]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"Streaming API call failed: {str(e)}")


class ZhipuAIClient(BaseLLMClient):
    """Client for ZhipuAI API"""

    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=api_key)
        except ImportError:
            raise ImportError("zhipuai package is required. Install with: pip install zhipuai")

    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"ZhipuAI API call failed: {str(e)}")

    def chat_stream(self, messages: List[Dict], temperature: float = 0.7) -> Generator[str, None, None]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"ZhipuAI streaming API call failed: {str(e)}")


class LLMClient:
    """Unified LLM Client factory"""

    PROVIDER_MAP = {
        'zhipu': ZhipuAIClient,
        'kimi': OpenAICompatibleClient,
        'deepseek': OpenAICompatibleClient,
        'doubao': OpenAICompatibleClient
    }

    def __init__(self, provider: str, api_key: str, model: str = None, base_url: str = None):
        """
        Initialize LLM client

        Args:
            provider: Provider name ('zhipu', 'kimi', 'deepseek', 'doubao')
            api_key: API key
            model: Model name (optional, uses default if not provided)
            base_url: Base URL for API (required for kimi, deepseek)
        """
        from config import Config

        if provider not in self.PROVIDER_MAP:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(self.PROVIDER_MAP.keys())}")

        provider_config = Config.LLM_PROVIDERS.get(provider, {})

        # Use default model if not provided
        if model is None:
            model = provider_config.get('default_model')

        # Get base_url from config if not provided
        if base_url is None:
            base_url = provider_config.get('base_url')

        # Create appropriate client
        client_class = self.PROVIDER_MAP[provider]

        if provider in ['kimi', 'deepseek', 'doubao']:
            self.client = client_class(api_key, model, base_url)
        else:
            self.client = client_class(api_key, model)

    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """Send chat request and return response"""
        return self.client.chat(messages, temperature, max_tokens)

    def chat_stream(self, messages: List[Dict], temperature: float = 0.7) -> Generator[str, None, None]:
        """Send chat request and return streaming response"""
        return self.client.chat_stream(messages, temperature)


def get_available_providers() -> Dict:
    """Get list of available providers and their models"""
    from config import Config
    return Config.LLM_PROVIDERS
