from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, StringConstraints

Filename255 = Annotated[str, StringConstraints(min_length=1, max_length=255)]
S3Key512 = Annotated[str, StringConstraints(min_length=1, max_length=512)]


#  Requests
class DocumentIn(BaseModel):
    filename: Filename255
    size_bytes: int


class DocumentUpdate(BaseModel):
    filename: Optional[Filename255] = None
    size_bytes: Optional[int] = None


#  Response
class DocumentOut(BaseModel):
    id: int
    project_id: int
    filename: str
    s3_key: S3Key512
    size_bytes: int
    uploaded_by: Optional[int] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
