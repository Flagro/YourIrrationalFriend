import tiktoken
from typing import AsyncIterator
from openai import OpenAI


class AI:
    def __init__(
        self,
        openai_api_key: str,
        default_text_model_name: str,
        default_temperature: float = 0.7,
    ):
        self.client = OpenAI(api_key=openai_api_key)
        self.default_text_model_name = default_text_model_name
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
        response = self.client.chat.completions.create(
            model=self.default_text_model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            stream=True,
            temperature=self.default_temperature,
        )
        for chunk in response:
            chunk_text = chunk.choices[0].delta.content
            yield chunk_text
