import tiktoken
from typing import AsyncIterator, Literal
from openai import OpenAI


class AI:
    def __init__(self, openai_api_key: str, default_text_model_name: str):
        self.llm = OpenAI(api_key=openai_api_key, model=default_text_model_name)

    async def is_content_acceptable(self, text: str):
        # TODO: implement this
        # r = await openai.Moderation.acreate(input=text)
        # return not all(r.results[0].categories.values())
        return True

    @staticmethod
    def count_tokens(text: str):
        return tiktoken.count(text)

    async def get_streaming_reply(
        self, user_input: str, system_prompt: str
    ) -> AsyncIterator[str]:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input),
        ]
        temperature = (self.ai_config.TextGeneration.temperature,)
        for chunk in await self.llm.astream(messages, temperature=temperature):
            yield chunk.content
