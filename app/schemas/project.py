from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints

Name120 = Annotated[str, StringConstraints(min_length=1, max_length=120)]

# Requests
class ProjectIn(BaseModel):
    name: Name120
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[Name120] = None
    description: Optional[str] = None


# Response
class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)