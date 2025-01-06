from typing import Any

from pydantic import ValidationError

from models.chat_message import ChatMessage, DataExtracted, SearchResult, StoryResult


def get_last_user_message(messages: list[ChatMessage]) -> ChatMessage | None:
    for message in reversed(messages):
        if message.type == "user":
            return message
    return None


def get_last_bot_message(messages: list[ChatMessage]) -> ChatMessage | None:
    for message in reversed(messages):
        if message.type == "bot":
            return message
    return None


def validate_step(step: dict) -> Any:
    # Check for the type of step and validate accordingly
    if step["type"] == "extracted":
        return DataExtracted.model_validate(step)
    if step["type"] == "searchResult":
        return SearchResult.model_validate(step)
    if step["type"] == "storyResult":
        return StoryResult.model_validate(step)
    raise ValidationError(f"Invalid step type: {step['type']}")
