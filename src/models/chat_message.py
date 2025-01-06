from pydantic import BaseModel


# Model for DataExtracted's `data` field
class DataExtractedData(BaseModel):
    theme: str
    genre: str
    tone: str
    key_elements: list[str]
    language: str


# Model for SearchResult's `data` field
class SearchResultData(BaseModel):
    title: str
    url: str
    description: str


# Model for StoryResult's `data` field
class StoryResultData(BaseModel):
    title: str
    content: str
    image: str


# Define the step models
class DataExtracted(BaseModel):
    type: str = "extracted"
    data: DataExtractedData  # Nested model for the `data` field


class SearchResult(BaseModel):
    type: str = "searchResult"
    data: list[SearchResultData]  # List of SearchResultData


class StoryResult(BaseModel):
    type: str = "storyResult"
    data: StoryResultData  # Nested model for the `data` field


StepType = DataExtracted | SearchResult | StoryResult


class ChatMessage(BaseModel):
    id: str
    content: str
    type: str  # Either "user" or "bot"
    steps: list[StepType]
