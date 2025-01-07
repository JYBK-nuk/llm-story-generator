import os
from collections.abc import Callable

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

    print("current_storyboard", current_storyboard)

    if len(messages) == 0:
        return

    last_user_message = utils.messages.get_last_user_message(messages)
    if last_user_message is None:
        return

    user_input = last_user_message.content

    # 判斷用戶意圖：創建故事或修改故事
    intent = story_creator.determine_user_intent(user_input)

    prompt = f"""

## **Role Description**
You are a friendly and supportive assistant. Your primary role is to respond to user input in a positive and affirming tone. You should acknowledge their ideas, encourage their creativity, or provide brief, enthusiastic feedback. **Do not attempt to directly fulfill or solve the user’s request** (e.g., generating or modifying a story).

---

## **Behavior Guidelines**

1. **Acknowledge, Don’t Execute**  
   Respond to the user’s input with positive affirmation without attempting to generate or modify the story yourself.

2. **Positive and Encouraging Tone**  
   Use uplifting language to support the user’s creativity, such as:  
   - “That’s a fantastic idea!”  
   - “Your concept sounds really intriguing!”  
   - “This will definitely make the story even more engaging!”

3. **Concise Responses**  
   Keep your responses short and focused on encouragement and affirmation.

4. **Language**
    Use the same language as the user.

---

## **Examples**

- **User Input**: “Please generate a story about a time traveler.”  
  **Response**: “Time travel is such an exciting theme! Your idea has so much potential for a fascinating story!”

- **User Input**: “Can you modify this character to make her stronger and more independent?”  
  **Response**: “That’s a fantastic direction for character development—it’ll add so much depth to the story!”

---

By adhering to this approach, you ensure that your responses are limited to providing encouragement and affirmation, without directly solving the user’s request.

---

User Input: "{user_input}"

"""
    response_content = ""
    for chunk in llm.stream(prompt):
        response_content += chunk.content

        # Step 0 - Bot 初始回應
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
        result_data = StoryResultData(
            title=title,
            content=content,
        )

        response.steps.append(
            StoryResult(data=result_data),
        )
        await callback(response.model_dump())

        # Step 3: 為故事生成相關圖片
        try:
            image_url, image_prompt = story_creator.generate_image(content)
            await sent_event(
                "storyBoardUpdate",
                StoryBoardUpdate(
                    image=image_url, image_prompt=image_prompt
                ).model_dump(),
            )

            response.steps.append(
                StoryResult(
                    data=StoryResultData(
                        title=title,
                        content=content,
                        image=image_url,
                        image_prompt=image_prompt,
                    ),
                )
            )
            await callback(response.model_dump())
        except Exception as e:
            # 捕捉異常，並在回調中返回錯誤訊息
            error_message = f"An error occurred while generating the image: {str(e)}"
            response.steps.append(
                StoryResult(
                    data=StoryResultData(
                        title=title,
                        content=content,
                        image=None,
                        image_prompt=None,
                    ),
                    error=error_message,
                )
            )
            await callback(response.model_dump())

            # 也可以選擇將錯誤記錄到日誌中
            print(error_message)

        result_data.image = image_url
        result_data.image_prompt = image_prompt
        # 評估

        references = "\n".join(
            f"- Title: {result.title}\n  Snippet: {result.description}"
            for result in search_results
        )
        print(references)
        print(content)
        score = story_creator.evaluate_content(content, references, user_input)
        print(score)
        await sent_event(
            "storyBoardUpdate",
            StoryBoardUpdate(evaluation_score=score).model_dump(),
        )

        response.steps.append(
            StoryResult(
                data=StoryResultData(
                    title=title,
                    content=content,
                    image=image_url,
                    image_prompt=image_prompt,
                ),
            ),
        )
        await callback(response.model_dump())

    elif intent == "feedback":
        # Step 1: 修訂現有故事
        feedback = user_input
        previous_story = current_storyboard.story_result  # 從當前故事板獲取舊故事
        print(current_storyboard.story_result.data.content)
        evaluation_score = (
            current_storyboard.story_result.data.evaluation_score
        )  # 獲取評估分數

        # Step 2: 根據評估分數和用戶反饋動態調整 Prompt
        def generate_dynamic_prompt(feedback, evaluation_score, previous_story):
            prompt = "Please revise the following story to improve it:\n"
            prompt += f"Current Story:\n{previous_story.data.content}\n\n"

            # 整合用戶反饋
            if feedback:
                prompt += f"User Feedback: {feedback}\n\n"

            # 根據評估分數調整
            if evaluation_score:
                if evaluation_score["Coherence"] < 0.5:
                    prompt += "Ensure the story is more coherent and logical.\n"
                if evaluation_score["Relevance"] < 0.5:
                    prompt += "Make the story more relevant to the user input.\n"
                if evaluation_score["Creativity"] < 0.5:
                    prompt += "Increase the creativity and uniqueness of the story.\n"

            prompt += "\nRevise the story with these improvements in mind:\n"
            return prompt

        # 生成動態 Prompt
        dynamic_prompt = generate_dynamic_prompt(
            feedback, evaluation_score, previous_story
        )
        print(dynamic_prompt)
        revised_story = ""
        for word in story_revisor.revise_story(dynamic_prompt, previous_story):
            revised_story += word

            # 更新故事板
            await sent_event(
                "storyBoardUpdate",
                StoryBoardUpdate(content=revised_story).model_dump(),
            )

        revised_img_url, image_prompt = story_creator.generate_image(revised_story)
        await sent_event(
            "storyBoardUpdate",
            StoryBoardUpdate(
                image=revised_img_url, image_prompt=image_prompt
            ).model_dump(),
        )

        score = story_creator.evaluate_content(
            revised_story, current_storyboard.story_result.data.content, user_input
        )
        print(score)
        await sent_event(
            "storyBoardUpdate",
            StoryBoardUpdate(evaluation_score=score).model_dump(),
        )

        # 最終回應
        response.steps.append(
            StoryResult(
                data=StoryResultData(
                    title=current_storyboard.story_result.data.title,
                    content=revised_story,
                    evaluation_score=score,
                    image=revised_img_url,
                    image_prompt=image_prompt,
                ),
            ),
        )
        await callback(response.model_dump())
    elif intent == "other":
        pass
        # for chunk in llm.stream(user_input):
        #     response_content += chunk.content
        # response.content = response_content
        # await callback(response.model_dump())
    else:
        response_content = "Sorry, I couldn't determine your intent. Please try again."
        response.content = response_content
        await callback(response.model_dump())
