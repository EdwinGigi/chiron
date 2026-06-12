from typing import TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from chiron.config import get_settings

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    """Wrapper around Google GenAI SDK for structured outputs."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_structured(
        self, prompt: str, schema: type[T], model: str = "gemini-2.5-flash"
    ) -> T:
        """Generate structured output matching a Pydantic schema."""
        # Using the async client generator
        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        # In newer versions of the SDK, response.parsed contains the Pydantic instance
        if hasattr(response, "parsed") and response.parsed is not None:
            return response.parsed

        # Fallback to manual parsing if response.parsed isn't populated
        import json

        data = json.loads(response.text)
        return schema(**data)  # type: ignore[no-any-return]
