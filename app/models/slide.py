from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SlideResult(BaseModel):
    title: str
    url: str
    author: Optional[str] = None
    description: Optional[str] = None
    views: Optional[int] = None
    slides: Optional[int] = None
    upload_date: Optional[str] = None
    page: int
    extracted_at: str = ""

    def model_post_init(self, __context):
        if not self.extracted_at:
            self.extracted_at = datetime.utcnow().isoformat()


class SearchRequest(BaseModel):
    query: str
    max_pages: int = 3