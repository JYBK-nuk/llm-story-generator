from pydantic import BaseModel


class StoryBoard(BaseModel):
    title: str | None = None
    content: str | None = None
    image: str | None = None
