from pydantic import BaseModel, HttpUrl


class ExportRequest(BaseModel):
    webhook_url: HttpUrl


class ExportResult(BaseModel):
    delivered: bool
    run_count: int
    status_code: int | None = None
    error: str | None = None
