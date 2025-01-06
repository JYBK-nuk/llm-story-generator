import asyncio
from collections.abc import Callable
from pprint import pprint

import utils.messages
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
from models.story_board import StoryBoard


@ws.register_event("message")
async def handle_message_event(
    data: dict, callback: Callable, sent_event: Callable
) -> None:
    current_steps_data = data.get("currentSteps", [])
    current_steps = []
    for step in current_steps_data:
        step_obj = utils.messages.validate_step(step)
        current_steps.append(step_obj)

    messages = [ChatMessage.model_validate(item) for item in data.get("messages", [])]

    # 訊息紀錄 裡面包含全部 (所以盡量只送 content 給使用者，steps 可能只有近期一兩個要送，也可都不送)
    print("Messages:")
    pprint(messages)
    # 左半邊目前的畫布 (真正給模型看現在文章內容及參考資料的)
    print("Current steps:")
    pprint(current_steps)

    if len(messages) == 0:
        return
    last_user_message = utils.messages.get_last_user_message(messages)
    if last_user_message is None:
        return

    user_input = last_user_message.content  # User input

    # Step 0 - BotReply
    response_content = "Hi, I'm a bot."  # LLM reply
    response = ChatMessage(
        id=last_user_message.id, type="bot", content=response_content, steps=[]
    )
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
    await sent_event("storyBoardUpdate", StoryBoard(title="title").model_dump())

    for _ in range(100):
        await asyncio.sleep(0.01)
        await sent_event("storyBoardUpdate", StoryBoard(content="content").model_dump())

    await sent_event("storyBoardUpdate", StoryBoard(image="image").model_dump())

    # Finally, send the response
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
