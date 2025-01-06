from pydantic import BaseModel, Field


# Model for DataExtracted's `data` field
class DataExtractedData(BaseModel):
    theme: str = Field(description="The main topic or subject")
    genre: str = Field(description="The type of story, e.g., Sci-fi, Fantasy, etc")
    tone: str = Field(description="The mood or attitude, e.g., Optimistic, Dark, etc")
    key_elements: list[str] = Field(
        description="Specific characters, locations, or plot points",
    )
    language: str = Field(description="The language of the input sentence")


# Model for SearchResult's `data` field
class SearchResultData(BaseModel):
    title: str
    url: str
    description: str


# Model for StoryResult's `data` field
class StoryResultData(BaseModel):
    title: str = Field(description="The title of the story")
    content: str = Field(description="The generated story content")
    image: str = ""
    image_prompt: str = ""


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
