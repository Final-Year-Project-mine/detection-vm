from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    path: str


class AnalyzeResponse(BaseModel):
    verdict: str
