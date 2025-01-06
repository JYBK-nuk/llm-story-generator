import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY,
)


def extract_story_details(input_sentence: str) -> dict:
    """
    使用語言模型從用戶輸入中提取主題、類型、語氣和關鍵要素
    """
    prompt = f"""
Extract the following details from the input sentence, and ensure the output uses the same language as the input:
Theme : The main topic or subject.
Genre : The type of story, e.g., Sci-fi, Fantasy, etc.
Tone : The mood or attitude, e.g., Optimistic, Dark, etc.
Key Elements : Specific characters, locations, or plot points.

Input: "{input_sentence}"
Theme: [The main topic or subject.]
Genre: [The type of story, e.g., Sci-fi, Fantasy, etc.]
Tone: [The mood or attitude, e.g., Optimistic, Dark, etc.]
Key Elements: [specific characters, locations, or plot points.] Elements separate by commas(,)
Language: [The language of the input sentence.]

"""
    # 調用模型生成輸出
    response = llm.invoke(prompt).content

    # 處理輸出為結構化數據
    lines = response.strip().split("\n")
    details = {}
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            details[key.strip()] = value.strip()

    if "Key Elements" in details:
        key_elements = details["Key Elements"]
        # 使用逗號或其他常見分隔符分割
        details["Key Elements"] = [elem.strip() for elem in key_elements.split(",")]

    print(f"Extracted details: {details}\n")

    return details


def google_search(query: str, num_results: int = 5) -> list:
    """
    使用 Google Custom Search API 搜索
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

    # 連接所有網站，並與查詢字串結合
    site_query = " OR ".join([f"site:{s}" for s in site])
    full_query = f"{query} {site_query}"
    # print(f"Full query: {full_query}")

    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "num": num_results,
        "lr": "lang_zh-TW",
        # "dateRestrict": "m3",  # 限制搜索結果為過去 3 個月
        "q": full_query,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Google Search API error: {response.text}")
    results = response.json()

    # 提取搜索結果
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
            {
                "title": title,
                "link": item.get("link", ""),
                "snippet": snippet,
                "og:description": og_description,
            },
        )

    return extracted_results


def generate_story_with_references(input_sentence: str) -> dict:
    """
    結合 Google 搜索結果生成故事
    """
    # 提取關鍵信息
    details = extract_story_details(input_sentence)
    theme = details.get("Theme", "")
    key_elements = " ".join(details.get("Key Elements", []))

    # Google 搜索
    query = f"{theme} {key_elements}"
    print(f"Google search query: {query}\n")
    search_results = google_search(query)
    print(f"Google search results: {search_results}\n")

    # 提取參考
    references = "\n".join(
        f"- Title: {result['title']}\n  Link: {result['link']}\n  Snippet: {result['snippet']}\n  Description: {result['og:description']}"
        for result in search_results
    )
    print(f"References:\n{references}\n")

    # 故事生成提示
    prompt = f"""
Use the following information to write a compelling {details.get("Genre", "story")} :
- **Theme**: {theme}
- **Tone**: {details.get("Tone", "neutral")}
- **Key Elements**: {key_elements}
- **References**:
{references}

### Rule:
Use {details.get("Language", "the same language as the input")}

### Instructions:
1. Ensure the story aligns with the specified theme and tone.
2. Incorporate the key elements naturally into the plot.
3. Use the references for inspiration and factual grounding, but create an original narrative.

Now, craft the story:
"""

    # 使用 LLM 生成故事
    story = llm.invoke(prompt).content
    print(f"Generated story:\n{story}\n")
    return story


def revise_story_with_feedback(previous_story: str, feedback: str) -> str:
    """
    基於用戶反饋修改故事
    """
    prompt = f"""
The user provided feedback to revise the following story:

### Story:
{previous_story}

### Feedback:
{feedback}

Revise the story based on the feedback while maintaining the original tone and theme:
"""
    revised_story = llm.invoke(prompt).content
    print(f"Revised story:\n{revised_story}\n")
    return revised_story


def determine_user_intent(user_input: str) -> str:
    """
    使用 LLM 判斷用戶意圖（創建新故事或提供反饋）
    """
    intent_prompt = PromptTemplate(
        input_variables=["user_input", "context"],
        template="""
Based on the user's input and the context, determine if the user wants to:
1. Create a new story.
2. Provide feedback for an existing story.

Input: {user_input}

Answer with either 'create' or 'feedback'.
""",
    )

    intent_chain = intent_prompt | llm
    return intent_chain.invoke({"user_input": user_input}).content


def generate_image(story: str) -> str:
    """
    生成與故事相關的圖片
    """
    prompt = PromptTemplate(
        input_variables=["story"],
        template="Summarize this story and generate a short image description that matches the story. : {story}",
    )

    image_pipeline = prompt | llm
    image_description = image_pipeline.invoke({"story": story}).content
    print(f"Generated image description: {image_description}\n")

    # 調用圖像生成模型生成圖片
    dalle_wrapper = DallEAPIWrapper()
    image_url = dalle_wrapper.run(image_description)
    print(f"Generated image URL: {image_url}\n")

    return image_url


if __name__ == "__main__":
    try:
        user_input = "一名科學家完成了一項AI實驗，造就了人類便利的未來。"
        intent = determine_user_intent(user_input)
        print(f"User intent: {intent}\n")
        if intent == "create":
            story = generate_story_with_references(user_input)
            generate_image(story)

        # user_input = "希望增加人類與AI合作的具體情節。"
        # intent = determine_user_intent(user_input)

    except Exception as e:
        print(e)


@router.post("/generate-story")
def generate_story(input_sentence: str) -> dict:
    try:
        story = generate_story_with_references(input_sentence)
        return {"story": story}
    except Exception as e:
        return {"error": str(e)}


@router.post("/revise-story")
def revise_story(previous_story: str, feedback: str) -> dict:
    try:
        revised_story = revise_story_with_feedback(previous_story, feedback)
        return {"revised_story": revised_story}
    except Exception as e:
        return {"error": str(e)}


@router.post("/generate-image")
def generate_image_endpoint(story: str) -> dict:
    try:
        image_url = generate_image(story)
        return {"image_url": image_url}
    except Exception as e:
        return {"error": str(e)}


@router.post("/determine-intent")
def determine_intent(user_input: str) -> dict:
    try:
        intent = determine_user_intent(user_input)
        return {"intent": intent}
    except Exception as e:
        return {"error": str(e)}


# @router.post("/extract-keywords")
# def extract_keywords(input_sentence: str) -> dict:
#     """
#     提取故事的關鍵元素
#     """
#     return extract_story_details(input_sentence)


# @router.post("/google-search")
# def search_google(query: str) -> dict:
#     """
#     使用 Google API 搜索內容並返回結果
#     """
#     try:
#         results = google_search(query)
#         return {"results": results}  # 將列表封裝在字典中
#     except Exception as e:
#         return {"error": str(e)}
