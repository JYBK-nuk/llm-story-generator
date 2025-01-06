import os
from collections.abc import Callable
from pprint import pprint

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

import utils.messages
from api.socketio import ws
from api.story.story import StoryCreator, StoryRevisor
from models.chat_message import (
    ChatMessage,
    DataExtracted,
    SearchResult,
    StoryResult,
    StoryResultData,
)
from models.story_board import StoryBoard, StoryBoardUpdate

load_dotenv()  # take environment variables from .env.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY,
)

# 初始化 StoryCreator 和 StoryRevisor
story_creator = StoryCreator(llm)
story_revisor = StoryRevisor(llm)


@ws.register_event("message")
async def handle_message_event(
    data: dict,
    callback: Callable,
    sent_event: Callable,
) -> None:
    """
    處理 WebSocket 消息事件，依據用戶意圖生成或修訂故事。
    """
    current_storyboard = StoryBoard.model_validate(data.get("currentStoryBoard", {}))
    messages = [ChatMessage.model_validate(item) for item in data.get("messages", [])]

    # 訊息紀錄
    print("Messages:")
    pprint(messages)

    # 當前故事板
    print("Current Storyboard:")
    pprint(current_storyboard)

    if len(messages) == 0:
        return

    last_user_message = utils.messages.get_last_user_message(messages)
    if last_user_message is None:
        return

    user_input = last_user_message.content

    # 判斷用戶意圖：創建故事或修改故事
    intent = story_creator.determine_user_intent(user_input)

    # Step 0 - Bot 初始回應
    response_content = "Hi, I'm a bot. Let's create or revise a story!"
    response = ChatMessage(
        id=last_user_message.id,
        type="bot",
        content=response_content,
        steps=[],
    )
    await callback(response.model_dump())

    # 根據意圖處理
    if intent == "create":
        # Step 1: 提取故事細節
        extracted_data = story_creator.extract_story_details(user_input)
        response.steps.append(DataExtracted(data=extracted_data))
        await callback(response.model_dump())

        current_storyboard.data_extracted = extracted_data

        # Step 2: 搜索相關資料
        search_results = story_creator.google_search(extracted_data)
        response.steps.append(
            SearchResult(
                data=search_results,
            ),
        )
        await callback(response.model_dump())

        current_storyboard.search_result = search_results

        # Step 3: 生成故事

        # await sent_event(
        #     "storyBoardUpdate",
        #     StoryBoardUpdate(
        #         title=generated_story.title,
        #     ).model_dump(),
        # )
        title = ""
        for worrd in story_creator.generate_title(extracted_data, search_results):
            title += worrd
            await sent_event(
                "storyBoardUpdate",
                StoryBoardUpdate(
                    title=title,
                ).model_dump(),
            )
        response.steps.append(
            StoryResult(
                data=StoryResultData(
                    title=title,
                    content="",
                    image="",
                ),
            ),
        )

        content = ""
        for word in story_creator.generate_story(extracted_data, search_results):
            content += word
            await sent_event(
                "storyBoardUpdate",
                StoryBoardUpdate(
                    content=content,
                ).model_dump(),
            )

        response.steps.append(
            StoryResult(
                data=StoryResultData(
                    title=title,
                    content=content,
                    image="",
                ),
            ),
        )

        current_storyboard.story_result = StoryResultData(
            title=title,
            content=content,
            image="",
        )

        # Step 3: 為故事生成相關圖片
        image_url = story_creator.generate_image(content)
        await sent_event(
            "storyBoardUpdate",
            StoryBoardUpdate(image=image_url).model_dump(),
        )

        await callback(response.model_dump())
        current_storyboard.story_result = StoryResultData(
            title=title,
            content=content,
            image=image_url,
        )
    elif intent == "feedback":

        # Step 1: 修訂現有故事
        feedback = user_input
        previous_story = current_storyboard.story_result  # 從當前故事板獲取舊故事
        revised_story = ""
        for word in story_revisor.revise_story(feedback, previous_story):
            revised_story += word

            # 更新故事板
            await sent_event(
                "storyBoardUpdate",
                StoryBoardUpdate(content=revised_story).model_dump(),
            )

        revised_img_url = story_creator.generate_image(revised_story)
        await sent_event(
            "storyBoardUpdate",
            StoryBoardUpdate(image=revised_img_url).model_dump(),
        )

        # 最終回應
        response.steps.append(
            StoryResult(
                data=StoryResultData(
                    title=current_storyboard.story_result.data.title,
                    content=revised_story,
                    image=revised_img_url,
                ),
            ),
        )
        await callback(response.model_dump())

    else:
        response_content = "Sorry, I couldn't determine your intent. Please try again."
        response.content = response_content
        await callback(response.model_dump())
