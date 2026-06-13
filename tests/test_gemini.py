from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from chiron.ai.gemini import GeminiClient


class DummySchema(BaseModel):
    name: str
    age: int


@pytest.fixture
def mock_settings():
    with patch("chiron.ai.gemini.get_settings") as mock_get_settings:
        mock_settings_obj = MagicMock()
        mock_settings_obj.gemini_api_key = "test_key"
        mock_get_settings.return_value = mock_settings_obj
        yield mock_get_settings


@pytest.fixture
def mock_gemini_client():
    with patch("chiron.ai.gemini.genai.Client") as mock_client:
        yield mock_client


@pytest.mark.asyncio
async def test_generate_structured_with_parsed(mock_gemini_client, mock_settings):
    # Setup mock
    client_instance = mock_gemini_client.return_value
    aio_mock = MagicMock()
    client_instance.aio = aio_mock
    models_mock = AsyncMock()
    aio_mock.models = models_mock

    # Mock response
    mock_response = MagicMock()
    mock_response.parsed = DummySchema(name="Test", age=30)
    models_mock.generate_content.return_value = mock_response

    # Test
    client = GeminiClient()
    result = await client.generate_structured("prompt", DummySchema)

    assert isinstance(result, DummySchema)
    assert result.name == "Test"
    assert result.age == 30
    models_mock.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_structured_fallback_parsing(mock_gemini_client, mock_settings):
    # Setup mock
    client_instance = mock_gemini_client.return_value
    aio_mock = MagicMock()
    client_instance.aio = aio_mock
    models_mock = AsyncMock()
    aio_mock.models = models_mock

    # Mock response without parsed attribute but with text
    mock_response = MagicMock()
    del mock_response.parsed
    mock_response.text = '{"name": "Fallback", "age": 40}'
    models_mock.generate_content.return_value = mock_response

    # Test
    client = GeminiClient()
    result = await client.generate_structured("prompt", DummySchema)

    assert isinstance(result, DummySchema)
    assert result.name == "Fallback"
    assert result.age == 40
    models_mock.generate_content.assert_called_once()
