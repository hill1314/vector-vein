# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-12-12 15:24:15
# @Last Modified by:   Bi Ying
# @Last Modified time: 2024-07-04 22:50:08
import json

from openai import OpenAI, AsyncOpenAI
from openai._types import NotGiven, NOT_GIVEN
from openai._streaming import Stream, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from utilities.config import Settings
from .base_client import BaseChatClient, BaseAsyncChatClient
from .utils import (
    tool_use_re,
    cutoff_messages,
    generate_tool_use_system_prompt,
    extract_tool_calls,
)


MODEL_MAX_INPUT_LENGTH = {
    "deepseek-chat": 128000,
    "deepseek-coder": 128000,
}


# 深度搜索聊天客户端
class DeepSeekChatClient(BaseChatClient):
    DEFAULT_MODEL: str = "deepseek-chat"

    def __init__(
        self,
        model: str = "deepseek-chat",
        stream: bool = True,
        temperature: float = 0.7,
        context_length_control: str = "latest",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.model = model
        self.stream = stream
        self.temperature = temperature
        self.context_length_control = context_length_control
        settings = Settings()
        self._client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base,
        )

    def create_completion(
        self,
        messages: list = list,
        model: str | None = None,
        stream: bool | None = None,
        temperature: float | None = None,
        max_tokens: int = 2000,
        tools: list | NotGiven = NOT_GIVEN,
        tool_choice: str | NotGiven = NOT_GIVEN,
    ):
        if model is not None:
            self.model = model
        if stream is not None:
            self.stream = stream
        if temperature is not None:
            self.temperature = temperature

        if self.context_length_control == "latest":
            messages = cutoff_messages(messages, max_count=MODEL_MAX_INPUT_LENGTH[self.model], model=self.model)

        if tools:
            tools_str = json.dumps(tools, ensure_ascii=False, indent=None)
            additional_system_prompt = generate_tool_use_system_prompt(tools=tools_str)
            if messages[0].get("role") == "system":
                messages[0]["content"] += "\n\n" + additional_system_prompt
            else:
                messages.insert(0, {"role": "system", "content": additional_system_prompt})

        response: ChatCompletion | Stream[ChatCompletionChunk] = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=self.stream,
            temperature=self.temperature,
            max_tokens=max_tokens,
        )

        if self.stream:

            def generator():
                full_content = ""
                result = {}
                for chunk in response:
                    if len(chunk.choices) == 0:
                        continue
                    message = chunk.choices[0].delta.model_dump()
                    full_content += message["content"] if message["content"] else ""
                    if tools:
                        tool_call_data = extract_tool_calls(full_content)
                        if tool_call_data:
                            message["tool_calls"] = tool_call_data["tool_calls"]
                    if full_content in ("<", "<|", "<|▶", "<|▶|") or full_content.startswith("<|▶|>"):
                        message["content"] = ""
                        result = message
                        continue
                    yield message
                if result:
                    yield result

            return generator()
        else:
            result = {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump(),
            }
            if tools:
                tool_call_data = extract_tool_calls(result["content"])
                if tool_call_data:
                    result["tool_calls"] = tool_call_data["tool_calls"]
                    result["content"] = tool_use_re.sub("", result["content"])
            return result


class AsyncDeepSeekChatClient(BaseAsyncChatClient):
    DEFAULT_MODEL: str = "deepseek-chat"

    def __init__(
        self,
        model: str = "deepseek-chat",
        stream: bool = True,
        temperature: float = 0.7,
        context_length_control: str = "latest",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.model = model
        self.stream = stream
        self.temperature = temperature
        self.context_length_control = context_length_control
        settings = Settings()
        self._client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base,
        )

    async def create_completion(
        self,
        messages: list = list,
        model: str | None = None,
        stream: bool | None = None,
        temperature: float | None = None,
        max_tokens: int = 2000,
        tools: list | NotGiven = NOT_GIVEN,
        tool_choice: str | NotGiven = NOT_GIVEN,
    ):
        if model is not None:
            self.model = model
        if stream is not None:
            self.stream = stream
        if temperature is not None:
            self.temperature = temperature

        if self.context_length_control == "latest":
            messages = cutoff_messages(messages, max_count=MODEL_MAX_INPUT_LENGTH[self.model], model=self.model)

        if tools:
            tools_str = json.dumps(tools, ensure_ascii=False, indent=None)
            additional_system_prompt = generate_tool_use_system_prompt(tools=tools_str)
            if messages[0].get("role") == "system":
                messages[0]["content"] += "\n\n" + additional_system_prompt
            else:
                messages.insert(0, {"role": "system", "content": additional_system_prompt})

        response: ChatCompletion | AsyncStream[ChatCompletionChunk] = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=self.stream,
            temperature=self.temperature,
            max_tokens=max_tokens,
        )

        if self.stream:

            async def generator():
                full_content = ""
                result = {}
                async for chunk in response:
                    if len(chunk.choices) == 0:
                        continue
                    message = chunk.choices[0].delta.model_dump()
                    full_content += message["content"] if message["content"] else ""
                    if tools:
                        tool_call_data = extract_tool_calls(full_content)
                        if tool_call_data:
                            message["tool_calls"] = tool_call_data["tool_calls"]
                    if full_content in ("<", "<|", "<|▶", "<|▶|") or full_content.startswith("<|▶|>"):
                        message["content"] = ""
                        result = message
                        continue
                    yield message
                if result:
                    yield result

            return generator()
        else:
            result = {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump(),
            }
            if tools:
                tool_call_data = extract_tool_calls(result["content"])
                if tool_call_data:
                    result["tool_calls"] = tool_call_data["tool_calls"]
                    result["content"] = tool_use_re.sub("", result["content"])
            return result
