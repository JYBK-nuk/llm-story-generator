from pydantic import BaseModel
from typing import Dict, Optional
from models.chat_message import DataExtracted, SearchResult, StoryResult


class StoryBoardUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    image: str | None = None
    evaluation_score: Optional[Dict[str, float]] = None


class StoryBoard(BaseModel):
    data_extracted: DataExtracted | None = None
    search_result: SearchResult | None = None
    story_result: StoryResult | None = None
