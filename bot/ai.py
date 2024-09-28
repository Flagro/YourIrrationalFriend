import tiktoken
from typing import AsyncIterator, Literal
from openai import OpenAI


class AI:
    def __init__(self, openai_api_key: str, default_text_model_name: str, default_temperature: float = 0.7):
        self.llm = OpenAI(api_key=openai_api_key, model=default_text_model_name)
        self.default_temperature = default_temperature

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
        if not self.is_content_acceptable(user_input):
            yield "I'm sorry, I can't respond to that."
            return
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input),
        ]
        for chunk in await self.llm.astream(messages, temperature=self.default_temperature):
            yield chunk.content
