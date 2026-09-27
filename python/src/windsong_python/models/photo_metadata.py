from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    content: str = Field(min_length=1, max_length=30000)


class PhotoDraft(BaseModel):
    index: int
    status: str = "ready"
    url: str = ""
    thumbnail: str = ""
    title: str = ""
    description: str = ""
    date: str = ""
    location: str = ""
    city: str = ""
    country: str = ""
    tags: list[str] = Field(default_factory=list)
    aspectRatio: str = ""
    warnings: list[str] = Field(default_factory=list)
    missingFields: list[str] = Field(default_factory=list)


class ParseResponse(BaseModel):
    items: list[PhotoDraft]
