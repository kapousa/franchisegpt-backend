from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str
    model: str = "mistral"  # default is mistral, but you can override
