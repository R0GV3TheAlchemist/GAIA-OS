from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    gaian_slug: Optional[str] = None
    enable_web_search: bool = True
    max_sources: int = 8


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    enable_web_search: bool = False
    schumann_hz: float = 7.83


class CreateGaianRequest(BaseModel):
    name: str
    base_form: Optional[str] = "gaia"
    personality: Optional[str] = None
    avatar_color: Optional[str] = None
    user_name: Optional[str] = None


class BirthRequest(BaseModel):
    name: str
    user_name: Optional[str] = None
    user_gender: str = "unknown"
    birth_date: Optional[str] = None
    base_form: str = "gaia"
    personality: Optional[str] = None
    avatar_color: Optional[str] = None
    user_id: str = "anonymous"


class RememberRequest(BaseModel):
    memory: str


class VisibleMemoryRequest(BaseModel):
    memory: str


class SetGaianRequest(BaseModel):
    gaian_slug: str


class ConsentRequest(BaseModel):
    collective_consent: bool
