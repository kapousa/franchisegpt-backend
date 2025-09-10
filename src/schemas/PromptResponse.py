from pydantic import BaseModel
from typing import List

class PromptResponse(BaseModel):
    answer: str
    context: List[str]
