import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from models.chat_message import DataExtractedData, StoryResultData

load_dotenv()  # take environment variables from .env.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY,
)


# def extract_story_details(input_sentence: str) -> DataExtractedData:
#     """
#     使用語言模型從用戶輸入中提取主題、類型、語氣和關鍵要素
#     """
#     prompt = f"""
# Extract the following details from the input sentence, and ensure the output uses the same language as the input:

# Input: "{input_sentence}"
# """
#     # 調用模型生成輸出
#     response = llm.with_structured_output(DataExtractedData).invoke(prompt)

#     print(f"Extracted details: {response}\n")
#     return response


# def google_search(query: str, num_results: int = 5) -> list:
#     """
#     使用 Google Custom Search API 搜索
#     """
#     url = "https://www.googleapis.com/customsearch/v1"

#     site = [
#         "https://tw.news.yahoo.com/",
#         "https://udn.com/",
#         "https://www.ettoday.net/",
#         "https://news.tvbs.com.tw/",
#         "https://www.ltn.com.tw/",
#         "https://www.chinatimes.com/",
#         "https://www.setn.com/",
#         "https://news.ebc.net.tw/",
#         "https://www.nownews.com/",
#         "https://www.storm.mg/",
#     ]

#     # 連接所有網站，並與查詢字串結合
#     site_query = " OR ".join([f"site:{s}" for s in site])
#     full_query = f"{query} {site_query}"
#     # print(f"Full query: {full_query}")

#     params = {
#         "key": GOOGLE_API_KEY,
#         "cx": GOOGLE_CX,
#         "num": num_results,
#         "lr": "lang_zh-TW",
#         # "dateRestrict": "m3",  # 限制搜索結果為過去 3 個月
#         "q": full_query,
#     }
#     response = requests.get(url, params=params)
#     if response.status_code != 200:
#         raise Exception(f"Google Search API error: {response.text}")
#     results = response.json()

#     # 提取搜索結果
#     extracted_results = []
#     for item in results.get("items", []):
#         title = item.get("title", "")
#         snippet = item.get("snippet", "")
#         link = item.get("link", "")
#         # 嘗試從 metatags 提取 og:description
#         og_description = ""
#         pagemap = item.get("pagemap", {})
#         if "metatags" in pagemap:
#             metatags = pagemap.get("metatags", [{}])[0]
#             og_description = metatags.get("og:description", "")

#         extracted_results.append(
#             {
#                 "title": title,
#                 "link": item.get("link", ""),
#                 "snippet": snippet,
#                 "og:description": og_description,
#             },
#         )

#     return extracted_results


# def generate_story_with_references(input_sentence: str) -> dict:
#     """
#     結合 Google 搜索結果生成故事
#     """
#     # 提取關鍵信息
#     details = extract_story_details(input_sentence)
#     key_elements = " ".join(details.key_elements)

#     # Google 搜索
#     query = f"{details.theme} {key_elements}"
#     print(f"Google search query: {query}\n")
#     search_results = google_search(query)
#     print(f"Google search results: {search_results}\n")

#     # 提取參考
#     references = "\n".join(
#         f"- Title: {result['title']}\n  Link: {result['link']}\n  Snippet: {result['snippet']}\n  Description: {result['og:description']}"
#         for result in search_results
#     )
#     print(f"References:\n{references}\n")

#     # 故事生成提示
#     prompt = f"""
# Use the following information to write a compelling {details.genre}:
# - **Theme**: {details.theme}
# - **Tone**: {details.tone}
# - **Key Elements**: {key_elements}
# - **References**:
# {references}

# ### Rule:
# Use {details.language}

# ### Instructions:
# 1. Ensure the story aligns with the specified theme and tone.
# 2. Incorporate the key elements naturally into the plot.
# 3. Use the references for inspiration and factual grounding, but create an original narrative.

# Now, craft the story:
# """

#     story = llm.with_structured_output(StoryResultData).invoke(prompt)
#     print(f"Generated story:\n{story}\n")
#     return story


# def revise_story_with_feedback(previous_story: str, feedback: str) -> str:
#     """
#     基於用戶反饋修改故事
#     """
#     prompt = f"""
# The user provided feedback to revise the following story:

# ### Story:
# {previous_story}

# ### Feedback:
# {feedback}

# Revise the story based on the feedback while maintaining the original tone and theme:
# """
#     revised_story = llm.with_structured_output(StoryResultData).invoke(prompt)
#     print(f"Revised story:\n{revised_story}\n")
#     return revised_story


# def determine_user_intent(user_input: str) -> str:
#     """
#     使用 LLM 判斷用戶意圖（創建新故事或提供反饋）
#     """
#     intent_prompt = PromptTemplate(
#         input_variables=["user_input", "context"],
#         template="""
# Based on the user's input and the context, determine if the user wants to:
# 1. Create a new story.
# 2. Provide feedback for an existing story.

# Input: {user_input}

# Answer with either 'create' or 'feedback'.
# """,
#     )

#     intent_chain = intent_prompt | llm
#     return intent_chain.invoke({"user_input": user_input}).content


# def generate_image(story: str) -> str:
#     """
#     生成與故事相關的圖片
#     """
#     prompt = PromptTemplate(
#         input_variables=["story"],
#         template="Summarize this story and generate a short image description that matches the story. : {story}",
#     )

#     image_pipeline = prompt | llm
#     image_description = image_pipeline.invoke({"story": story}).content
#     print(f"Generated image description: {image_description}\n")

#     # 調用圖像生成模型生成圖片
#     dalle_wrapper = DallEAPIWrapper()
#     image_url = dalle_wrapper.run(image_description)
#     print(f"Generated image URL: {image_url}\n")

#     return image_url


class BaseStoryProcessor:
    """
    基底類別，封裝共用的故事處理功能
    """

    def __init__(self, llm):
        self.llm = llm

    def extract_story_details(self, input_sentence: str) -> DataExtractedData:
        """
        使用 LLM 提取故事細節
        """
        prompt = f"""
Extract the following details from the input sentence, and ensure the output uses the same language as the input:

Input: "{input_sentence}"
"""

        return self.llm.with_structured_output(DataExtractedData).invoke(prompt)

    def google_search(self, query: str, num_results: int = 5) -> list:
        """
        執行 Google 搜索
        """
        url = "https://www.googleapis.com/customsearch/v1"
        site = [
            "https://tw.news.yahoo.com/",
            "https://udn.com/",
            "https://www.ettoday.net/",
            "https://news.tvbs.com.tw/",
            "https://www.ltn.com.tw/",
            "https://www.chinatimes.com/",
            "https://www.setn.com/",
            "https://news.ebc.net.tw/",
            "https://www.nownews.com/",
            "https://www.storm.mg/",
        ]
        site_query = " OR ".join([f"site:{s}" for s in site])
        full_query = f"{query} {site_query}"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CX,
            "num": num_results,
            "lr": "lang_zh-TW",
            "q": full_query,
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Google Search API error: {response.text}")
        return response.json().get("items", [])

    def generate_image(self, story: str) -> str:
        """
        為故事生成相關圖片
        """
        prompt = PromptTemplate(
            input_variables=["story"],
            template="Generate an image description for the following story: {story}",
        )
        image_pipeline = prompt | llm
        image_description = image_pipeline.invoke({"story": story}).content

        dalle_wrapper = DallEAPIWrapper()

        return dalle_wrapper.run(image_description)

    def determine_user_intent(self, user_input: str) -> str:
        """
        判斷用戶意圖
        """
        prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""Determine if the input is for:
1. Creating a new story.
2. Providing feedback for an existing story.

Input: {user_input}

Answer 'create' or 'feedback'.
""",
        )

        intent_pipeline = prompt | llm
        return intent_pipeline.invoke({"user_input": user_input}).content


class StoryCreator(BaseStoryProcessor):
    """
    負責創建新故事的處理鏈
    """

    def generate_story(self, input_sentence: str) -> StoryResultData:
        """
        結合搜索結果生成故事
        """
        details = self.extract_story_details(input_sentence)
        key_elements = " ".join(details.key_elements)
        query = f"{details.theme} {key_elements}"
        search_results = self.google_search(query)

        references = "\n".join(
            f"- Title: {item.get('title')}\n  Link: {item.get('link')}\n  Description: {item.get('snippet')}"
            for item in search_results
        )

        prompt = f"""
Use the following information to write a compelling {details.genre}:
- **Theme**: {details.theme}
- **Tone**: {details.tone}
- **Key Elements**: {key_elements}
- **References**:
{references}

### Rule:
Use {details.language}

### Instructions:
1. Align with the theme and tone.
2. Use key elements in the plot.
3. Reference factual details but ensure originality.

Generate the story:
"""

        return self.llm.with_structured_output(StoryResultData).invoke(prompt).content


class StoryRevisor(BaseStoryProcessor):
    """
    負責修改故事的處理鏈
    """

    def revise_story(self, previous_story: str, feedback: str) -> str:
        """
        基於反饋修改故事
        """
        prompt = f"""
The user provided feedback to revise the following story:

### Story:
{previous_story}

### Feedback:
{feedback}

Revise the story based on the feedback, keeping the original tone and theme:
"""

        return self.llm.with_structured_output(StoryResultData).invoke(prompt).content


if __name__ == "__main__":
    # 初始化 StoryCreator 和 StoryRevisor
    story_creator = StoryCreator(llm)
    story_revisor = StoryRevisor(llm)

    # 測試創建新故事
    print("===== 測試創建新故事 =====")
    input_sentence = (
        "一名科學家無意中開啟了一扇通往魔法世界的門，徹底改變了現實世界的規則。"
    )
    generated_story = story_creator.generate_story(input_sentence)
    print("生成的故事：")
    print(generated_story)

    # 測試生成故事圖片
    print("\n===== 測試生成故事圖片 =====")
    story_image_url = story_creator.generate_image(generated_story)
    print(f"生成的圖片 URL: {story_image_url}")

    # 測試修改故事
    print("\n===== 測試修改故事 =====")
    input_sentence = "希望故事中加入更多具體場景。"
    feedback = story_revisor.determine_user_intent(input_sentence)
    revised_story = story_revisor.revise_story(generated_story, feedback)
    print("修改後的故事：")
    print(revised_story)

    # 測試生成故事圖片
    print("\n===== 測試生成故事圖片 =====")
    story_image_url = story_creator.generate_image(revised_story)
    print(f"生成的圖片 URL: {story_image_url}")

# @router.post("/generate-story")
# def generate_story(input_sentence: str) -> dict:
#     try:
#         story = generate_story_with_references(input_sentence)
#         return {"story": story}
#     except Exception as e:
#         return {"error": str(e)}


# @router.post("/revise-story")
# def revise_story(previous_story: str, feedback: str) -> dict:
#     try:
#         revised_story = revise_story_with_feedback(previous_story, feedback)
#         return {"revised_story": revised_story}
#     except Exception as e:
#         return {"error": str(e)}


# @router.post("/generate-image")
# def generate_image_endpoint(story: str) -> dict:
#     try:
#         image_url = generate_image(story)
#         return {"image_url": image_url}
#     except Exception as e:
#         return {"error": str(e)}


# @router.post("/determine-intent")
# def determine_intent(user_input: str) -> dict:
#     try:
#         intent = determine_user_intent(user_input)
#         return {"intent": intent}
#     except Exception as e:
#         return {"error": str(e)}
