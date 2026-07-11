import asyncio
from google import genai
from google.genai import types
from google.genai.client import HttpRetryOptions
from app.config import settings

class LLMService:
    def __init__(self):
        self._client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options={
                "retry_options": HttpRetryOptions(attempts=1)
            }
        )
        self._model = "gemini-flash-lite-latest"

    async def generate(
        self,
        user_message: str,
        history: list[dict],
        system_prompt: str | None = None,
    ) -> str:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt or settings.default_system_prompt,
            max_output_tokens=1024,
            temperature=0.75,
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
            ]
        )
        chat = self._client.chats.create(
            model=self._model,
            history=history,
            config=config,
        )
        response = await asyncio.to_thread(chat.send_message, user_message)
        if not response.text:
            raise ValueError("Gemini returned an empty response")
        return response.text

llm_service = LLMService()
