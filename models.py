from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SearchParameters(BaseModel):
    query: str = Field(..., description="Search term to look up")

class TranslateParameters(BaseModel):
    text: str
    target_language: str

class SummarizeParameters(BaseModel):
    text: str

class WeatherParameters(BaseModel):
    """Parameters for weather function"""
    city: str = Field(..., description="City name to get weather for")

class FunctionCall(BaseModel):
    name: str
    parameters: Dict[str, Any]

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str

    def to_string(self) -> str:
        return f"Title: {self.title}\nLink: {self.link}\nSnippet: {self.snippet}"