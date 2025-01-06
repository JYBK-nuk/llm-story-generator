from collections.abc import Awaitable, Callable
from typing import Any

from api.socketio import ws
from models.chat_message import (
    ChatMessage,
    DataExtracted,
    DataExtractedData,
    SearchResult,
    SearchResultData,
    StoryResult,
    StoryResultData,
)


@ws.register_event("message")
async def handle_message_event(data: list[dict], callback: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
    messages = [ChatMessage.model_validate(item) for item in data]
    if len(messages) == 0:
        return

    last_message = messages[-1]
    if last_message.type == "bot":
        return

    user_input = last_message.content  # User input

    # Step 0 - BotReply
    response_content = "Hi, I'm a bot."  # LLM reply
    response = ChatMessage(id=last_message.id, type="bot", content=response_content, steps=[])
    await callback(response.model_dump())

    # Step 1 - DataExtracted
    response.steps.append(
        DataExtracted(
            data=DataExtractedData(
                theme="theme",
                genre="genre",
                tone="tone",
                key_elements=["key_elements"],
                language="language",
            ),
        ),
    )
    await callback(response.model_dump())

    # Step 2 - SearchResult
    response.steps.append(
        SearchResult(
            data=[
                SearchResultData(
                    title="title",
                    url="url",
                    description="description",
                ),
                SearchResultData(
                    title="title",
                    url="url",
                    description="description",
                ),
                SearchResultData(
                    title="title",
                    url="url",
                    description="description",
                ),
            ],
        ),
    )

    await callback(response.model_dump())

    # Step 3 - StoryResult
    response.steps.append(
        StoryResult(
            data=StoryResultData(
                title="title",
                content="content",
                image="image",
            ),
        ),
    )

    await callback(response.model_dump())
