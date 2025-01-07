import os
from collections.abc import Iterable

import requests
from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from transformers import pipeline
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import numpy as np
from models.chat_message import DataExtractedData, SearchResultData

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


prompts = {
    "image_generation": """
Generate prompts for image generation with DALL·E 3 based on the following rules:

- Each prompt should describe a clear visual scene with specific details.
- Focus on tangible elements like setting, characters, colors, lighting, and composition.
- Use modifiers to adjust the mood, style, and atmosphere of the scene.
- Avoid abstract or emotional language, and keep the prompt concise.
- Prompt should always be written in English, regardless of the input language. Please provide the prompts in English.
- Each prompt should consist of a description of the scene followed by modifiers divided by commas.
- When generating descriptions, focus on portraying the visual elements rather than delving into abstract psychological and emotional aspects. Provide clear and concise details that vividly depict the scene and its composition, capturing the tangible elements that make up the setting.
- The modifiers should alter the mood, style, lighting, and other aspects of the scene.
- Multiple modifiers can be used to provide more specific details.

Example:

1. A ghostly figure drifting through an eerie, candlelit ballroom, with shadows cast on the walls.
2. A fantasy archer with Homer Simpson’s face, shooting arrows at a forest monster in a dark, cinematic style.
3. A pirate standing on a stormy ship deck, sharp details, dramatic lighting, and vivid colors.
4. A Western cinematic scene with god rays and dramatic clouds, inspired by Red Dead Redemption 2.
5. Portrait of a woman in bronze armor with an owl crown, in a fantasy RPG style with sharp focus and heroic lighting.
6. Close-up of a biomechanical female warrior in a futuristic sci-fi environment, sleek lines, high-tech details.
7. Ultra-realistic portrait of Steve Urkel transformed into the Hulk, with intense details and smooth textures.
8. A vibrant anime-style portrait of Ana de Armas, with soft lines, bright colors, and sharp focus.
9. A surreal scene with tropical fruits on a table, with water droplets, abstract background, and bright lighting.
10. A magical hourglass with sand spilling out, glowing particles, and a mystical nebula background.
11. Geometric, colorful background with a woman at the center, glowing skin, dynamic angles, and zentangle patterns.

I want you to write me **a** prompt for generating an image based on the following story:

STORY: {story}
""",
}


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

    def google_search(self, details: DataExtractedData, num_results: int = 5) -> list:
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

        key_elements = " ".join(details.key_elements)
        query = f"{details.theme} {key_elements}"
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

        results = response.json()
        extracted_results = []
        for item in results.get("items", []):
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            # 嘗試從 metatags 提取 og:description
            og_description = ""
            pagemap = item.get("pagemap", {})
            if "metatags" in pagemap:
                metatags = pagemap.get("metatags", [{}])[0]
                og_description = metatags.get("og:description", "")

            extracted_results.append(
                SearchResultData.model_validate(
                    {
                        "title": title,
                        "url": item.get("link", ""),
                        "description": max(
                            snippet,
                            og_description,
                            key=len,
                        ),
                    },
                ),
            )

        return extracted_results

    def evaluate_content(
        self,
        generated_text: str,
        reference_text: str,
        user_input: str = None,
    ) -> dict:
        if not isinstance(generated_text, str):
            raise TypeError(
                f"Expected generated_text to be a string, got {type(generated_text)}"
            )
        if not isinstance(reference_text, str):
            raise TypeError(
                f"Expected reference_text to be a string, got {type(reference_text)}"
            )
        # BLEU Score (Relevance to Reference Text)
        reference_tokens = [reference_text.split()]
        generated_tokens = generated_text.split()
        smooth = SmoothingFunction().method1  # 添加平滑處理
        bleu_score = sentence_bleu(reference_tokens, generated_tokens)

        # Coherence (Semantic Similarity with User Input)
        model = SentenceTransformer("all-MiniLM-L6-v2")
        if user_input is not None:
            user_embedding = model.encode([user_input])
            generated_embedding = model.encode([generated_text])
            coherence_score = (
                None
                if user_input is None
                else cosine_similarity(user_embedding, generated_embedding)[0][0]
            )
        else:
            coherence_score = 0

        # Relevance (Semantic Similarity with Reference Text)
        reference_embedding = model.encode([reference_text])
        generated_embedding = model.encode([generated_text])
        relevance_score = cosine_similarity(reference_embedding, generated_embedding)[
            0
        ][0]

        # Creativity (Sentiment and Diversity)
        sentiment = TextBlob(generated_text).sentiment
        unique_words = len(set(generated_tokens))
        diversity = (
            unique_words / len(generated_tokens) if len(generated_tokens) > 0 else 0
        )

        return {
            "BLEU": bleu_score,
            "Coherence": coherence_score,
            "Relevance": relevance_score,
            "Creativity": diversity,
        }

    def generate_image(self, story: str) -> tuple[str, str]:
        """
        為故事生成相關圖片
        """
        prompt = PromptTemplate(
            input_variables=["story"],
            template=prompts["image_generation"],
        )
        image_pipeline = prompt | llm
        image_description = image_pipeline.invoke({"story": story}).content
        print("Image Description: ", image_description)
        dalle_wrapper = DallEAPIWrapper(model="dall-e-3")

        return dalle_wrapper.run(image_description), image_description

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

    def generate_title(
        self,
        details: DataExtractedData,
        search_results: list[SearchResultData],
    ) -> Iterable[str]:
        """
        生成故事標題
        """

        references = "\n".join(
            f"- Title: {result.title}\n  Link: {result.url}\n  Snippet: {result.description}"
            for result in search_results
        )

        prompt = f"""
Use the following information to write a story title
- **Theme**: {details.theme}
- **genre=**: {details.genre}
- **Tone**: {details.tone}
- **Key Elements**: {" ".join(details.key_elements)}
- **References**:
{references}

### Rule:
Use {details.language}.
Don't use Markdown syntax.

### Instructions:
1. Align with the theme and tone.
2. Use key elements in the plot.
3. Reference factual details but ensure originality.

Generate the story title:
"""
        for chunk in self.llm.stream(prompt):
            yield (chunk.content)

    def generate_story(
        self,
        details: DataExtractedData,
        search_results: list[SearchResultData],
    ) -> Iterable[str]:
        """
        結合搜索結果生成故事
        """

        references = "\n".join(
            f"- Title: {result.title}\n  Link: {result.url}\n  Snippet: {result.description}"
            for result in search_results
        )

        prompt = f"""
Use the following information to write a compelling {details.genre}:
- **Theme**: {details.theme}
- **Tone**: {details.tone}
- **Key Elements**: {" ".join(details.key_elements)}
- **References**:
{references}

### Rule:
Use {details.language}D
Only include the story content.

### Instructions:
1. Align with the theme and tone.
2. Use key elements in the plot.
3. Reference factual details but ensure originality.

Generate the story :
"""
        for chunk in self.llm.stream(prompt):
            yield (chunk.content)


class StoryRevisor(BaseStoryProcessor):
    """
    負責修改故事的處理鏈
    """

    def revise_story(self, previous_story: str, feedback: str) -> Iterable[str]:
        """
        基於反饋修改故事
        """
        prompt = f"""
The user provided feedback to revise the following story:

### Rule:
Use the same language as the original story, unless the feedback suggests otherwise.
Only include the story content.

### Story:
{previous_story}

### Feedback:
{feedback}

Revise the story based on the feedback, keeping the original tone and theme:
"""

        for chunk in self.llm.stream(prompt):
            yield (chunk.content)


if __name__ == "__main__":
    # 初始化 StoryCreator 和 StoryRevisor
    story_creator = StoryCreator(llm)
    story_revisor = StoryRevisor(llm)

    # 測試創建新故事
    print("===== 測試創建新故事 =====")
    input_sentence = (
        "一名科學家無意中開啟了一扇通往魔法世界的門，徹底改變了現實世界的規則。"
    )

    # 提取故事細節
    extracted_data = story_creator.extract_story_details(input_sentence)
    print("提取的故事細節：")
    print(extracted_data)

    # 搜索相關資料
    search_results = story_creator.google_search(extracted_data)
    print("搜索結果：")
    print(search_results)

    # 生成故事
    generated_story = story_creator.generate_story(extracted_data, search_results)
    # print("生成的故事：")
    # print(generated_story)

    # # 測試生成故事圖片
    # print("\n===== 測試生成故事圖片 =====")
    # story_image_url, _ = story_creator.generate_image(generated_story)
    # print(f"生成的圖片 URL: {story_image_url}")

    # # 測試修改故事
    # print("\n===== 測試修改故事 =====")
    # input_sentence = "希望故事中加入更多具體場景。"
    # feedback = story_revisor.determine_user_intent(input_sentence)
    # revised_story = story_revisor.revise_story(generated_story, feedback)
    # print("修改後的故事：")
    # print(revised_story)

    # # 測試生成故事圖片
    # print("\n===== 測試生成故事圖片 =====")
    # story_image_url, _ = story_creator.generate_image(revised_story)
    # print(f"生成的圖片 URL: {story_image_url}")
