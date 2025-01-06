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
from models.story_board import StoryBoard, StoryBoardUpdate


@ws.register_event("message")
async def handle_message_event(data: dict, callback: Callable, sent_event: Callable) -> None:
    current_storyboard = StoryBoard.model_validate(data.get("currentStoryBoard", {}))
    messages = [ChatMessage.model_validate(item) for item in data.get("messages", [])]

    # 訊息紀錄 裡面包含全部 (所以盡量只送 content 給使用者，steps 可能只有近期一兩個要送，也可都不送)
    print("Messages:")
    pprint(messages)
    # 左半邊目前的畫布 (真正給模型看現在文章內容及參考資料的)
    print("Current Storyboard:")
    pprint(current_storyboard)

    if len(messages) == 0:
        return
    last_user_message = utils.messages.get_last_user_message(messages)
    if last_user_message is None:
        return

    user_input = last_user_message.content  # User input

    # Step 0 - BotReply
    response_content = "Hi, I'm a bot."  # LLM reply
    response = ChatMessage(id=last_user_message.id, type="bot", content=response_content, steps=[])
    await asyncio.sleep(3)
    await callback(response.model_dump())

    # Step 1 - DataExtracted
    response.steps.append(
        DataExtracted(
            data=DataExtractedData(
                theme="AI",
                genre="科幻",
                tone="輕鬆",
                key_elements=["AI", "改變", "生活"],
                language="zh-TW",
            ),
        ),
    )
    await asyncio.sleep(3)
    await callback(response.model_dump())
    # Step 2 - SearchResult
    response.steps.append(
        SearchResult(
            data=[
                SearchResultData(
                    title="AI 101",
                    url="https://www.example.com",
                    description="什麼 AI 已經改變了我們的生活，這是一個 AI 的基礎介紹。",
                ),
                SearchResultData(
                    title="Cybertruck 川普大樓前爆炸",
                    url="https://www.example.com",
                    description="在川普大樓前發生了 Cybertruck 爆炸事件，這是一個 Cybertruck 的新聞報導。",
                ),
                SearchResultData(
                    title="特斯拉 Cybertruck 爆炸事件",
                    url="https://www.example.com",
                    description="特斯拉 Cybertruck，這是一個 Cybertruck 的新聞報導。",
                ),
            ],
        ),
    )

    await asyncio.sleep(3)
    await callback(response.model_dump())
    # Step 3 - StoryResult
    await sent_event("storyBoardUpdate", StoryBoardUpdate(title="這是一個悲慘的專題故事").model_dump())

    mocked_content = """美國拉斯維加斯的川普酒店門口，1日有一輛特斯拉Cybertruck電動皮卡汽車爆炸，駕駛是一名現役綠扁帽特種部隊軍人，被發現時已自轟身亡，警方仍在調查作案動機，但最新消息指出，嫌犯6天前才與妻子發生激烈爭吵，隨後租車前往拉斯維加斯。
紐約郵報報導，根據熟悉調查情況的執法部門消息人士，37歲的李維爾斯貝格（Matthew Alan Livelsberger）因為外遇問題與妻子發生爭吵，耶誕節隔天就離開位在科羅拉多泉的住家。
消息指出，李維爾斯貝格與妻子育有1女，據報妻子向李維爾斯貝格說，自己知道他一直在偷吃。
拉斯維加斯警方稱，李維爾斯貝格離開科羅拉多泉後，透過Turo租了一輛Cybertruck前往拉斯維加斯，1日將車停在川普酒店前，引爆車內藏有的炸彈，隨後舉槍自戕。
隨著調查進一步進行，警調正在釐清李維爾斯貝格的犯案動機是否純粹出於個人原因，而非先前所推測的政治動機。
李維爾斯貝格是陸軍精銳特種部隊「綠扁帽」成員，2017年和2018年曾被部署到阿富汗，已在陸軍服役至少19年，以愛國主義出名，他的叔叔堅稱，「他愛川普，是個非常愛國的士兵，一個愛國的美國人。」"""

    for i in range(len(mocked_content)):
        await asyncio.sleep(0.01)
        await sent_event("storyBoardUpdate", StoryBoardUpdate(content=mocked_content[:i]).model_dump())

    await sent_event("storyBoardUpdate", StoryBoardUpdate(image="image").model_dump())

    # Finally, send the response
    response.steps.append(
        StoryResult(
            data=StoryResultData(
                title="這是一個悲慘的專題故事",
                content=mocked_content,
                image="image",
            ),
        ),
    )
    await callback(response.model_dump())
