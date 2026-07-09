from pydantic import BaseModel, Field


class ScriptParsed(BaseModel):
    script: str = Field(min_length=1, default="")
