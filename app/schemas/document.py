from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Filename255 = Annotated[str, StringConstraints(min_length=1, max_length=255)]
S3Key512 = Annotated[str, StringConstraints(min_length=1, max_length=512)]


#  Requests
class DocumentIn(BaseModel):
    filename: Filename255
    size_bytes: int


class DocumentUpdate(BaseModel):
    filename: Optional[Filename255] = None
    size_bytes: Optional[int] = None


#  Responses
class DocumentOut(BaseModel):
    id: int
    project_id: int
    filename: Filename255
    s3_key: S3Key512
    size_bytes: Optional[int] = None
    content_type: Optional[str] = None
    uploaded_by: Optional[int] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListOut(BaseModel):
    items: List[DocumentOut]
    total: int = Field(ge=0)
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=200, default=50)


class DocumentDownloadLinkOut(BaseModel):
    url: str
    expires_in: int = Field(ge=1)
